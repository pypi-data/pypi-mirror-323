from colorama import Fore, Style

def plus(a, b):
    c = a + b
    print(f"After adding {Fore.GREEN}{a}{Style.RESET_ALL} and {Fore.GREEN}{b}{Style.RESET_ALL}, the result is: {Fore.GREEN}{c}{Style.RESET_ALL}")
    
def minus(a, b):
    c = a - b
    print(f"After subtracting {Fore.RED}{b}{Style.RESET_ALL} from {Fore.RED}{a}{Style.RESET_ALL}, the result is: {Fore.RED}{c}{Style.RESET_ALL}")
