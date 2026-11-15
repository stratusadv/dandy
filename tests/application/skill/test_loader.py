import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from dandy.application.skill.loader import load_cli_skills, load_skill_files, parse_skill_file

ACTIVE_SKILL = '---\ndescription: Do the thing.\n---\nDo the thing.\n'

PASSIVE_SKILL = '---\ndescription: Do the thing on demand.\nactive: false\n---\nDo the thing.\n'


def write_skill(root: Path, skill_name: str, text: str) -> Path:
    skill_dir = root / skill_name
    skill_dir.mkdir(parents=True)
    skill_file = skill_dir / 'SKILL.md'
    skill_file.write_text(text, encoding='utf-8')
    return skill_file


class SkillDirsCase(TestCase):
    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp_dir.cleanup)
        self.base_path = Path(self._temp_dir.name)
        self.global_dir = self.base_path / 'global'
        self.project_dir = self.base_path / 'project'
        self.global_dir.mkdir()
        self.project_dir.mkdir()


class TestParseSkillFile(SkillDirsCase):
    def test_parses_frontmatter_and_body(self) -> None:
        frontmatter, body, issues = parse_skill_file(
            '---\nname: git\ndescription: Git ops.\nactive: false\n---\nWork with git.\n'
        )

        self.assertEqual(frontmatter, {'name': 'git', 'description': 'Git ops.', 'active': 'false'})
        self.assertEqual(body, 'Work with git.')
        self.assertEqual(issues, [])

    def test_keeps_unknown_keys_and_blank_lines(self) -> None:
        text = '---\nname: git\n\ncustom: value\n---\nBody.\n'
        frontmatter, body, issues = parse_skill_file(text)

        self.assertEqual(frontmatter, {'name': 'git', 'custom': 'value'})
        self.assertEqual(body, 'Body.')
        self.assertEqual(issues, [])

    def test_strips_matching_quotes_from_values(self) -> None:
        text = '---\nname: "git"\ndescription: \'Git ops.\'\n---\n'
        frontmatter, _body, issues = parse_skill_file(text)

        self.assertEqual(frontmatter, {'name': 'git', 'description': 'Git ops.'})
        self.assertEqual(issues, [])

    def test_missing_opening_fence(self) -> None:
        frontmatter, body, issues = parse_skill_file('Just a body.\n')

        self.assertEqual(frontmatter, {})
        self.assertEqual(body, '')
        self.assertEqual(len(issues), 1)
        self.assertIn('opening', issues[0])

    def test_empty_file(self) -> None:
        frontmatter, body, issues = parse_skill_file('')

        self.assertEqual(frontmatter, {})
        self.assertEqual(body, '')
        self.assertEqual(len(issues), 1)

    def test_missing_closing_fence(self) -> None:
        frontmatter, body, issues = parse_skill_file('---\nname: git\n')

        self.assertEqual(frontmatter, {})
        self.assertEqual(body, '')
        self.assertEqual(len(issues), 1)
        self.assertIn('closing', issues[0])

    def test_unrecognized_frontmatter_line(self) -> None:
        frontmatter, body, issues = parse_skill_file('---\nname: git\njunk\n---\nBody.\n')

        self.assertEqual(frontmatter, {'name': 'git'})
        self.assertEqual(body, 'Body.')
        self.assertEqual(issues, ['unrecognized frontmatter line: "junk"'])


class TestLoadSkillFiles(SkillDirsCase):
    def test_missing_directories_load_nothing(self) -> None:
        skills, issues = load_skill_files([self.base_path / 'nope', self.project_dir])

        self.assertEqual(skills, [])
        self.assertEqual(issues, [])

    def test_empty_directories_load_nothing(self) -> None:
        skills, issues = load_skill_files([self.global_dir, self.project_dir])

        self.assertEqual(skills, [])
        self.assertEqual(issues, [])

    def test_stray_files_and_skillless_folders_are_ignored(self) -> None:
        (self.global_dir / 'notes.txt').write_text('not a skill', encoding='utf-8')
        (self.project_dir / 'empty').mkdir()

        skills, issues = load_skill_files([self.global_dir, self.project_dir])

        self.assertEqual(skills, [])
        self.assertEqual(issues, [])

    def test_minimal_skill_defaults_to_folder_name_and_active(self) -> None:
        write_skill(self.project_dir, 'git', '---\n---\nWork with git.\n')

        skills, issues = load_skill_files([self.global_dir, self.project_dir])

        self.assertEqual(issues, [])
        self.assertEqual(len(skills), 1)
        self.assertEqual(skills[0].name, 'git')
        self.assertEqual(skills[0].description, '')
        self.assertEqual(skills[0].prompt, 'Work with git.')
        self.assertTrue(skills[0].active)
        self.assertEqual(skills[0].tools, [])

    def test_frontmatter_overrides_name_and_active(self) -> None:
        text = '---\nname: deploy\ndescription: Deploy it.\n---\nDeploy.\n'
        write_skill(self.project_dir, 'folder', text)

        skills, issues = load_skill_files([self.project_dir])

        self.assertEqual(issues, [])
        self.assertEqual(skills[0].name, 'deploy')
        self.assertEqual(skills[0].description, 'Deploy it.')
        self.assertTrue(skills[0].active)

    def test_passive_skill(self) -> None:
        write_skill(self.project_dir, 'deploy', PASSIVE_SKILL)

        skills, issues = load_skill_files([self.project_dir])

        self.assertEqual(issues, [])
        self.assertFalse(skills[0].active)
        self.assertEqual(skills[0].description, 'Do the thing on demand.')

    def test_later_directory_overrides_earlier_by_name(self) -> None:
        write_skill(self.global_dir, 'git', '---\ndescription: Global git.\n---\nGlobal prompt.\n')
        text = '---\ndescription: Project git.\n---\nProject prompt.\n'
        write_skill(self.project_dir, 'git', text)
        write_skill(self.project_dir, 'other', ACTIVE_SKILL)

        skills, issues = load_skill_files([self.global_dir, self.project_dir])

        self.assertEqual(issues, [])
        self.assertEqual([skill.name for skill in skills], ['git', 'other'])
        self.assertEqual(skills[0].description, 'Project git.')
        self.assertEqual(skills[0].prompt, 'Project prompt.')

    def test_skills_are_sorted_by_name(self) -> None:
        write_skill(self.global_dir, 'zeta', ACTIVE_SKILL)
        write_skill(self.global_dir, 'alpha', ACTIVE_SKILL)
        write_skill(self.project_dir, 'mid', ACTIVE_SKILL)

        skills, _issues = load_skill_files([self.global_dir, self.project_dir])

        self.assertEqual([skill.name for skill in skills], ['alpha', 'mid', 'zeta'])

    def test_missing_opening_fence_is_an_issue(self) -> None:
        skill_file = write_skill(self.project_dir, 'broken', 'No frontmatter here.\n')

        skills, issues = load_skill_files([self.global_dir, self.project_dir])

        self.assertEqual(skills, [])
        self.assertEqual(len(issues), 1)
        self.assertIn(str(skill_file), issues[0])

    def test_missing_closing_fence_is_an_issue(self) -> None:
        skill_file = write_skill(self.project_dir, 'broken', '---\nname: broken\n')
        write_skill(self.project_dir, 'good', ACTIVE_SKILL)

        skills, issues = load_skill_files([self.global_dir, self.project_dir])

        self.assertEqual([skill.name for skill in skills], ['good'])
        self.assertEqual(len(issues), 1)
        self.assertIn(str(skill_file), issues[0])

    def test_passive_without_description_is_an_issue(self) -> None:
        skill_file = write_skill(self.project_dir, 'silent', '---\nactive: false\n---\nBody.\n')

        skills, issues = load_skill_files([self.project_dir])

        self.assertEqual(skills, [])
        self.assertEqual(len(issues), 1)
        self.assertIn('description', issues[0])
        self.assertIn(str(skill_file), issues[0])

    def test_explicit_empty_name_is_an_issue(self) -> None:
        skill_file = write_skill(self.project_dir, 'named', '---\nname: ""\n---\nBody.\n')

        skills, issues = load_skill_files([self.project_dir])

        self.assertEqual(skills, [])
        self.assertEqual(issues, [f'{skill_file}: empty skill name'])

    def test_unrecognized_active_value_is_an_issue(self) -> None:
        write_skill(self.project_dir, 'weird', '---\nactive: sometimes\n---\nBody.\n')

        skills, issues = load_skill_files([self.project_dir])

        self.assertEqual(skills, [])
        self.assertEqual(len(issues), 1)
        self.assertIn('active', issues[0])

    def test_empty_body_is_an_issue(self) -> None:
        write_skill(self.project_dir, 'hollow', '---\ndescription: No body.\n---\n   \n')

        skills, issues = load_skill_files([self.project_dir])

        self.assertEqual(skills, [])
        self.assertEqual(len(issues), 1)
        self.assertIn('empty skill prompt', issues[0])


class TestLoadCliSkills(SkillDirsCase):
    def test_composes_global_home_and_project_directories(self) -> None:
        fake_home = self.base_path / 'home'
        fake_global = fake_home / '.config' / 'dandy' / 'skills'
        write_skill(fake_global, 'global_only', ACTIVE_SKILL)
        write_skill(fake_global, 'shared', '---\n---\nGlobal shared.\n')

        project_base = self.base_path / 'repo'
        project_base.mkdir()
        write_skill(project_base / '.dandy' / 'skills', 'shared', '---\n---\nProject shared.\n')

        with patch('pathlib.Path.home', return_value=fake_home):
            skills, issues = load_cli_skills(project_base)

        self.assertEqual(issues, [])
        self.assertEqual([skill.name for skill in skills], ['global_only', 'shared'])
        self.assertEqual(skills[1].prompt, 'Project shared.')

    def test_missing_directories_load_nothing(self) -> None:
        fake_home = self.base_path / 'home'

        with patch('pathlib.Path.home', return_value=fake_home):
            skills, issues = load_cli_skills(self.base_path / 'nowhere')

        self.assertEqual(skills, [])
        self.assertEqual(issues, [])
