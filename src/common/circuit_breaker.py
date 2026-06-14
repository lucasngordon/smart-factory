import time


class CircuitBreaker:

    def __init__(self, max_falhas=3, tempo_recuperacao=30):

        self.max_falhas = max_falhas
        self.tempo_recuperacao = tempo_recuperacao

        self.falhas = 0
        self.aberto = False
        self.ultima_falha = None

    def call(self, func, *args, **kwargs):

        if self.aberto:

            tempo_passado = (
                time.time() - self.ultima_falha
            )

            if tempo_passado < self.tempo_recuperacao:

                print(
                    "[CircuitBreaker] Circuito aberto"
                )
                return

            print(
                "[CircuitBreaker] Tentando recuperação..."
            )

            self.aberto = False

        try:

            resultado = func(*args, **kwargs)

            self.falhas = 0

            return resultado

        except Exception as e:

            self.falhas += 1

            print(
                f"[CircuitBreaker] Falha {self.falhas}: {e}"
            )

            if self.falhas >= self.max_falhas:

                self.aberto = True
                self.ultima_falha = time.time()

                print(
                    "[CircuitBreaker] CIRCUITO ABERTO"
                )

            raise