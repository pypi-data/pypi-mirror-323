from pymnz import utils
import sys
import os


@utils.classes.singleton
class Script:
    def __init__(self, name, code):
        self.name = name
        self.code = code
        self.execution_interval = 10
        self.execution_interval_msg = 'Executando novamente em'
        self.width = 80
        self.separator_format = '='
        self.terminator_format = 'x'
        self.terminator_msg = 'Fim do script'

    def _show_header(self):
        """Amostrar cabeçalho"""
        print(self.separator_format * self.width)
        print(str(self.name).upper().center(self.width))
        print(self.separator_format * self.width)

    def _run_code(self):
        """Rodar código"""
        self.code()
        print(self.separator_format * self.width)

    @utils.errors.retry_on_failure(1000)
    def _run_code_with_retry_on_failure(self):
        """Rodar código com repetição por falha"""
        self._run_code()

    def run(self, with_retry_on_failure: bool = True):
        # Limpar console
        os.system('cls')

        self._show_header()

        try:
            while True:
                # Com repetição por falha
                if with_retry_on_failure:
                    self._run_code_with_retry_on_failure()

                # Sem repetição por falha
                else:
                    self._run_code()

                # Aguardar o intervalo
                utils.times.countdown_timer(
                    self.execution_interval, self.execution_interval_msg)

        except KeyboardInterrupt:
            print(self.terminator_format * self.width)
            sys.exit(self.terminator_msg)
