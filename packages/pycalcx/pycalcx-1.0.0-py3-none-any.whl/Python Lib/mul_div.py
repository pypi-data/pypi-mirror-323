from colorama import Fore, Style

def multiply(a, b):
    c = a * b
    print(f"After multiplying {Fore.YELLOW}{a}{Style.RESET_ALL} and {Fore.YELLOW}{b}{Style.RESET_ALL}, the result is: {Fore.YELLOW}{c}{Style.RESET_ALL}")

def divide(a, b):
    if b == 0:
        print(f"{Fore.RED}Error: Division by zero is not allowed!{Style.RESET_ALL}")
    else:
        c = a / b
        print(f"After dividing {Fore.BLUE}{a}{Style.RESET_ALL} by {Fore.BLUE}{b}{Style.RESET_ALL}, the result is: {Fore.BLUE}{c}{Style.RESET_ALL}")
