import tidi

def get_audience() -> str:
    return "World"

@tidi.inject
class Welcomer:
    def __init__(self, audience: tidi.Injected[str] = tidi.Provider(get_audience)):
        self.audience = audience

    def greet(self):
        print(f"Hello, {self.audience}! 👋")

def main():
    welcomer = Welcomer()
    welcomer.greet()

if __name__ == "__main__":
    main()
