import random
import matplotlib.pyplot as plt
from collections import deque
import sys

class RouletteSimulator:
    def __init__(self, balance, bet_amounts, system, max_spins=1000, wheel_type='American'):
        """
        Initialize the Roulette Simulator.

        :param balance: Starting balance for the player.
        :param bet_amounts: Dictionary containing bet amounts for different sections or a single bet amount.
        :param system: Betting system to use ('Martingale', 'Reverse Martingale', 'Custom', 'Fibonacci').
        :param max_spins: Maximum number of spins to simulate.
        :param wheel_type: Type of roulette wheel ('European' or 'American').
        """
        self.balance = balance
        self.initial_balance = balance
        self.bet_amounts = bet_amounts  # For custom systems or single bet amount
        self.system = system
        self.max_spins = max_spins
        self.current_bet = bet_amounts if isinstance(bet_amounts, dict) else bet_amounts
        self.spin_results = []
        self.history = []
        self.balance_over_time = []
        self.wins = 0
        self.losses = 0

        # Define wheel ranges based on wheel type
        if wheel_type == 'European':
            self.wheel_size = 37  # 0-36
            self.numbers = list(range(0, 37))
        elif wheel_type == 'American':
            self.wheel_size = 38  # 0-36 plus '00'
            self.numbers = [0, '00'] + list(range(1, 37))
        else:
            raise ValueError("wheel_type must be 'European' or 'American'")

        # Define sections
        self.sections = self.define_sections()

        # Initialize Fibonacci sequence if needed
        if self.system == 'Fibonacci':
            self.fib_sequence = deque([1, 1])  # Starting with two 1s
            self.fib_step = 0  # Current step in the Fibonacci sequence

    def define_sections(self):
        """
        Define the sections of the roulette wheel.

        :return: Dictionary with section names and their corresponding number ranges.
        """
        if self.system == 'Custom':
            # For Custom system, define thirds excluding 0 and 00
            # European wheel: numbers = [0] + 1-36
            # American wheel: numbers = [0, '00'] + 1-36
            # Exclude '00' if present
            numbers = [num for num in self.numbers if isinstance(num, int)]  # Exclude '00' if present
            third = len(numbers) // 3
            first_third = numbers[:third]       # 1-12
            second_third = numbers[third:2*third]  # 13-24
            third_third = numbers[2*third:]     # 25-36
            return {
                'first': first_third,
                'second': second_third,
                'third': third_third
            }
        else:
            return {}

    def spin_wheel(self):
        """
        Simulate spinning the roulette wheel.

        :return: The result of the spin.
        """
        return random.choice(self.numbers)

    def run(self):
        """
        Execute the simulation based on the selected betting system.

        :return: History of bets, final balance, balance over time, total wins, total losses.
        """
        spin = 0  # Initialize spin counter
        while spin < self.max_spins and self.balance > 0:
            spin += 1  # Increment spin counter

            if self.system == 'Martingale':
                # Martingale System: Double the bet after a loss
                current_bet = self.current_bet
                if self.balance < current_bet:
                    print(f"Spin {spin}: Insufficient balance to continue.")
                    break
                self.balance -= current_bet
                result = self.spin_wheel()
                self.spin_results.append(result)
                win = self.is_win(0, result)  # Betting on number 0

                if win:
                    payout = 35 * current_bet  # Payout for single number
                    self.balance += payout
                    self.history.append({
                        'spin': spin,
                        'bet': current_bet,
                        'result': result,
                        'outcome': 'Win',
                        'balance': self.balance
                    })
                    self.current_bet = self.bet_amounts  # Reset bet
                    self.wins += 1

                    # Prompt to continue
                    if not self.prompt_continue(spin):
                        break
                else:
                    self.history.append({
                        'spin': spin,
                        'bet': current_bet,
                        'result': result,
                        'outcome': 'Loss',
                        'balance': self.balance
                    })
                    self.current_bet *= 2  # Double the bet
                    self.losses += 1

            elif self.system == 'Reverse Martingale':
                # Reverse Martingale System: Double the bet after a win
                current_bet = self.current_bet
                if self.balance < current_bet:
                    print(f"Spin {spin}: Insufficient balance to continue.")
                    break
                self.balance -= current_bet
                result = self.spin_wheel()
                self.spin_results.append(result)
                win = self.is_win(0, result)  # Betting on number 0

                if win:
                    payout = 35 * current_bet
                    self.balance += payout
                    self.history.append({
                        'spin': spin,
                        'bet': current_bet,
                        'result': result,
                        'outcome': 'Win',
                        'balance': self.balance
                    })
                    self.current_bet *= 2  # Double the bet after a win
                    self.wins += 1

                    # Prompt to continue
                    if not self.prompt_continue(spin):
                        break
                else:
                    self.history.append({
                        'spin': spin,
                        'bet': current_bet,
                        'result': result,
                        'outcome': 'Loss',
                        'balance': self.balance
                    })
                    self.current_bet = self.bet_amounts  # Reset the bet after a loss
                    self.losses += 1

            elif self.system == 'Fibonacci':
                # Fibonacci System: Follow the Fibonacci sequence for bet sizes
                if self.fib_step >= len(self.fib_sequence):
                    # Extend the sequence
                    next_fib = self.fib_sequence[-1] + self.fib_sequence[-2]
                    self.fib_sequence.append(next_fib)

                current_bet = self.fib_sequence[self.fib_step] * self.bet_amounts  # Bet is multiple of base bet
                if self.balance < current_bet:
                    print(f"Spin {spin}: Insufficient balance to continue.")
                    break
                self.balance -= current_bet
                result = self.spin_wheel()
                self.spin_results.append(result)
                win = self.is_win(0, result)  # Betting on number 0

                if win:
                    payout = 35 * current_bet
                    self.balance += payout
                    self.history.append({
                        'spin': spin,
                        'bet': current_bet,
                        'result': result,
                        'outcome': 'Win',
                        'balance': self.balance
                    })
                    # Move two steps back in the Fibonacci sequence
                    if self.fib_step > 1:
                        self.fib_step -= 2
                    else:
                        self.fib_step = 0
                    self.wins += 1

                    # Prompt to continue
                    if not self.prompt_continue(spin):
                        break
                else:
                    self.history.append({
                        'spin': spin,
                        'bet': current_bet,
                        'result': result,
                        'outcome': 'Loss',
                        'balance': self.balance
                    })
                    self.fib_step += 1
                    self.losses += 1

            elif self.system == 'Custom':
                # Custom System Betting on Sections
                bets = self.bet_amounts  # Should be a dict with keys 'first', 'second', 'third'
                total_bet = bets.get('second', 0) + bets.get('third', 0)
                if self.balance < total_bet:
                    print(f"Spin {spin}: Insufficient balance to continue.")
                    break

                self.balance -= total_bet
                result = self.spin_wheel()
                self.spin_results.append(result)

                # Determine which section the result is in
                winning_section = None
                for section_name, numbers in self.sections.items():
                    if result in numbers:
                        winning_section = section_name
                        break

                # Calculate outcomes based on the winning section
                if winning_section == 'first':
                    # Player loses all bets on second and third
                    net = - (bets.get('second', 0) + bets.get('third', 0))
                elif winning_section == 'second':
                    # Player breaks even: Win on second third, lose on third
                    payout = 2 * bets.get('second', 0)  # 2:1 payout
                    net = payout - bets.get('third', 0)
                elif winning_section == 'third':
                    # Player wins on third third, loses on second
                    payout = 2 * bets.get('third', 0)  # 2:1 payout
                    net = payout - bets.get('second', 0)
                else:
                    # If the result is 0 or 00, player loses all bets
                    net = - (bets.get('second', 0) + bets.get('third', 0))

                # Update balance with net profit/loss
                self.balance += net

                # Record the history
                self.history.append({
                    'spin': spin,
                    'bet': {'second': bets.get('second', 0), 'third': bets.get('third', 0)},
                    'result': result,
                    'winning_section': winning_section if winning_section else 'None (0 or 00)',
                    'net': net,
                    'balance': self.balance
                })

                # Update win/loss counts based on net
                if net > 0:
                    self.wins += 1

                    # Prompt to continue
                    if not self.prompt_continue(spin):
                        break
                elif net < 0:
                    self.losses += 1
                # Note: No prompt on break-even (net == 0)

            else:
                raise ValueError(f"Unknown betting system: {self.system}")

            # Record balance over time for visualization
            self.balance_over_time.append(self.balance)

        return self.history, self.balance, self.balance_over_time, self.wins, self.losses

    def is_win(self, bet_number, spin_result):
        """
        Check if the bet is a win.

        :param bet_number: The number the player is betting on.
        :param spin_result: The result of the spin.
        :return: Boolean indicating a win or loss.
        """
        return bet_number == spin_result

    def prompt_continue(self, spin):
        """
        Prompt the user to decide whether to continue gambling after a win.

        :param spin: Current spin number.
        :return: Boolean indicating whether to continue (True) or stop (False).
        """
        print("\n--- Current Status ---")
        print(f"Spin Number: {spin}")
        print(f"Current Balance: ${self.balance:.2f}")
        print(f"Total Wins: {self.wins}")
        print(f"Total Losses: {self.losses}")
        if self.system in ['Martingale', 'Reverse Martingale', 'Fibonacci']:
            print(f"Current Bet: ${self.current_bet:.2f}")
            net = self.balance - self.initial_balance
            print(f"Net Profit/Loss: ${net:.2f}")
        elif self.system == 'Custom':
            print(f"Current Bet on Second Third: ${self.bet_amounts.get('second', 0):.2f}")
            print(f"Current Bet on Third Third: ${self.bet_amounts.get('third', 0):.2f}")
            net = self.balance - self.initial_balance
            print(f"Net Profit/Loss: ${net:.2f}")
        print("----------------------")

        while True:
            response = input("You won! Do you want to continue gambling? (yes/no): ").strip().lower()
            if response in ['yes', 'y']:
                return True
            elif response in ['no', 'n']:
                return False
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")

def get_user_input():
    """
    Gather user inputs for the simulation.

    :return: Tuple containing initial_balance, bet_amounts, system, max_spins, wheel_type.
    """
    print("Welcome to the Roulette Simulator!\n")

    # Get Initial Balance
    while True:
        try:
            initial_balance = float(input("Enter your initial balance (e.g., 1000): $"))
            if initial_balance <= 0:
                print("Initial balance must be greater than 0.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")

    # Choose Wheel Type
    wheel_types = ['European', 'American']
    print("\nChoose the type of roulette wheel:")
    for idx, wt in enumerate(wheel_types, 1):
        print(f"{idx}. {wt}")
    while True:
        try:
            wheel_choice = int(input("Enter the number corresponding to your choice: "))
            if 1 <= wheel_choice <= len(wheel_types):
                wheel_type = wheel_types[wheel_choice - 1]
                break
            else:
                print(f"Please enter a number between 1 and {len(wheel_types)}.")
        except ValueError:
            print("Please enter a valid number.")

    # Choose Betting System
    systems = ['Martingale', 'Reverse Martingale', 'Custom', 'Fibonacci']
    print("\nChoose a betting system:")
    for idx, sys_name in enumerate(systems, 1):
        print(f"{idx}. {sys_name}")
    while True:
        try:
            choice = int(input("Enter the number corresponding to your choice: "))
            if 1 <= choice <= len(systems):
                system = systems[choice - 1]
                break
            else:
                print(f"Please enter a number between 1 and {len(systems)}.")
        except ValueError:
            print("Please enter a valid number.")

    # Get Bet Amounts based on the system
    if system == 'Custom':
        print("\nConfigure your Custom Betting System:")
        print("You will specify bet amounts for the Second Third and Third Third.")
        print("First Third bet is $0 as per your strategy.")
        try:
            second_bet = float(input("Enter your bet amount for the Second Third (e.g., 5): $"))
            third_bet = float(input("Enter your bet amount for the Third Third (e.g., 10): $"))
            bet_amounts = {
                'first': 0,   # $0 on first third
                'second': second_bet,  # e.g., $5
                'third': third_bet     # e.g., $10
            }
        except ValueError:
            print("Invalid input. Please enter numeric values.")
            sys.exit(1)
    elif system == 'Fibonacci':
        print("\nConfigure your Fibonacci Betting System:")
        try:
            base_bet = float(input("Enter your base bet amount (e.g., 10): $"))
            if base_bet <= 0:
                print("Base bet must be greater than 0.")
                sys.exit(1)
            bet_amounts = base_bet
        except ValueError:
            print("Invalid input. Please enter a numeric value.")
            sys.exit(1)
    else:
        print(f"\nConfigure your {system} Betting System:")
        try:
            bet_amount = float(input("Enter your initial bet amount (e.g., 10): $"))
            if bet_amount <= 0:
                print("Bet amount must be greater than 0.")
                sys.exit(1)
            bet_amounts = bet_amount
        except ValueError:
            print("Invalid input. Please enter a numeric value.")
            sys.exit(1)

    # Get Number of Spins
    while True:
        try:
            max_spins = int(input("\nEnter the number of spins to simulate (e.g., 100): "))
            if max_spins <= 0:
                print("Number of spins must be greater than 0.")
                continue
            break
        except ValueError:
            print("Please enter a valid integer.")

    return initial_balance, bet_amounts, system, max_spins, wheel_type

def plot_results(balance_over_time, wins, losses, system):
    """
    Plot Balance Over Time and Win/Loss Distribution.

    :param balance_over_time: List of balance values after each spin.
    :param wins: Total number of wins.
    :param losses: Total number of losses.
    :param system: The betting system used.
    """
    fig, axs = plt.subplots(2, 1, figsize=(14, 10))

    # Plot Balance Over Time
    axs[0].plot(balance_over_time, color='blue', linewidth=1)
    axs[0].set_title(f'Balance Over Time - {system} System')
    axs[0].set_xlabel('Spin Number')
    axs[0].set_ylabel('Balance ($)')
    axs[0].grid(True)

    # Highlight starting balance
    axs[0].axhline(y=balance_over_time[0], color='green', linestyle='--', label='Initial Balance')
    axs[0].legend()

    # Plot Win/Loss Distribution
    labels = ['Wins', 'Losses']
    counts = [wins, losses]
    colors = ['green', 'red']
    axs[1].bar(labels, counts, color=colors)
    axs[1].set_title(f'Win/Loss Distribution - {system} System')
    axs[1].set_xlabel('Outcome')
    axs[1].set_ylabel('Count')
    for i, v in enumerate(counts):
        axs[1].text(i, v + max(counts)*0.01, str(v), ha='center', fontweight='bold')
    axs[1].set_ylim(0, max(counts)*1.1)

    plt.tight_layout()
    plt.show()

def main():
    # Gather user inputs
    initial_balance, bet_amounts, system, max_spins, wheel_type = get_user_input()

    # Initialize the simulator
    simulator = RouletteSimulator(
        balance=initial_balance,
        bet_amounts=bet_amounts,
        system=system,
        max_spins=max_spins,
        wheel_type=wheel_type  # User-selected wheel type
    )

    # Run the simulation
    history, final_balance, balance_over_time, wins, losses = simulator.run()

    # Display Results
    print("\n--- Simulation Results ---")
    print(f"Betting System: {system}")
    print(f"Wheel Type: {wheel_type}")
    print(f"Initial Balance: ${initial_balance}")
    print(f"Final Balance: ${final_balance}")
    print(f"Total Spins: {len(balance_over_time)}")
    print(f"Total Wins: {wins}")
    print(f"Total Losses: {losses}")
    print(f"Net Profit/Loss: ${final_balance - initial_balance}")

    # Plot the results
    plot_results(balance_over_time, wins, losses, system)

if __name__ == "__main__":
    main()

