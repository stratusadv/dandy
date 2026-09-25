from __future__ import annotations

import mkdocs_gen_files

from pathlib import Path


class APIReferenceGenerator:
    def __init__(self) -> None:
        self.navigation = mkdocs_gen_files.Nav()
        self.root = Path(__file__).parent.parent.parent
        self.source = self.root / 'dandy'

    @property
    def ignored(self) -> set[str]:
        return {
            '__pycache__',
            'migrations',
            'static',
            'templates',
            'tests'
        }

    def _process_module_path(self, path: Path) -> tuple[tuple[str, ...], Path, Path]:
        module = path.relative_to(self.root).with_suffix('')
        components = tuple(module.parts)

        if components[-1] == '__init__':
            components = components[:-1]
            document = path.relative_to(self.root).parent / 'index.md'
        else:
            document = path.relative_to(self.root).with_suffix('.md')

        full = Path('reference', document)
        return components, document, full

    def _should_skip_module(self, components: tuple[str, ...]) -> bool:
        return components[-1] == '__main__'

    def _should_skip_path(self, path: Path, ignored: set[str]) -> bool:
        return any(directory in path.parts for directory in ignored)

    def generate_documentation(self, components: tuple[str, ...], full: Path, path: Path) -> None:
        with mkdocs_gen_files.open(full, 'w') as handle:
            identifier = '.'.join(components)
            handle.write(f'::: {identifier}')

        mkdocs_gen_files.set_edit_path(full, path)

    def generate_navigation(self) -> None:
        with mkdocs_gen_files.open('reference/SUMMARY.md', 'w') as handle:
            navigation = self.navigation.build_literate_nav()
            handle.writelines(navigation)

    def generate_pages(self) -> None:
        files = self.source.rglob('*.py')

        for path in sorted(files):
            if self._should_skip_path(path, self.ignored):
                continue

            components, document, full = self._process_module_path(path)

            if self._should_skip_module(components):
                continue

            self.navigation[components] = document.as_posix()
            self.generate_documentation(components, full, path)

        self.generate_navigation()


generator = APIReferenceGenerator()
generator.generate_pages()
