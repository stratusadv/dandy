from dandy.calculator.llm_calculator import model_size_and_token_count_for_inference_to_vram_gb
from dandy.cli.commands.command import BaseCommand


class CalculateCommand(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--model-parameter-count-billions',
            type=int,
            required=True,
            help='The number of billions of model parameters to calculate for.'
        )

        parser.add_argument(
            '--quantization-size-bits',
            type=int,
        )

        parser.add_argument(
            '--tokens',
            type=int,
        )

    @property
    def help(self) -> str:
        return 'Calculate the model size and token count for inference to VRAM in GB.'

    def process(self, *args, **kwargs):
        return self.calculate(**kwargs)

    def calculate(
            self,
            model_parameter_count_billions: int,
            quantization_size_bits: int,
            token_count: int,
    ) -> float:
        return model_size_and_token_count_for_inference_to_vram_gb(
            model_parameter_count_billions,
            quantization_size_bits,
            token_count
        )
