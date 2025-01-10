import random
import matplotlib.pyplot as plt
from collections import deque
import sys

class RouletteSimulator:
    def __init__(
        self, 
        balance, 
        bet_amounts, 
        system, 
        max_spins=1000, 
        wheel_type='American', 
        prompt_after_win=True,
        bet_type='single'
    ):
        """
        Initialize the Roulette Simulator.

        :param balance: Starting balance for the player.
        :param bet_amounts: Dictionary containing bet amounts for different sections or a single bet amount.
        :param system: Betting system to use.
        :param max_spins: Maximum number of spins to simulate.
        :param wheel_type: Type of roulette wheel ('European' or 'American').
        :param prompt_after_win: If True, prompt user after every win to continue or stop. 
        :param bet_type: The type of bet coverage to simulate (e.g., 'single', 'split', 'corner', 'line', 'dozen', 'even-chance').
        """
        self.balance = balance
        self.initial_balance = balance
        self.bet_amounts = bet_amounts
        self.system = system
        self.max_spins = max_spins
        self.current_bet = bet_amounts if isinstance(bet_amounts, dict) else bet_amounts
        self.spin_results = []
        self.history = []
        self.balance_over_time = []
        self.wins = 0
        self.losses = 0
        self.prompt_after_win = prompt_after_win

        # For the new bet coverage
        self.bet_type = bet_type
        self.bet_numbers, self.bet_payout = self.define_bet_coverage(bet_type)

        # Track winning streaks
        self.current_streak = 0
        self.longest_streak = 0
        self.current_streak_winnings = 0.0
        self.longest_streak_winnings = 0.0

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

        # System-specific variables
        if self.system == 'Fibonacci':
            self.fib_sequence = deque([1, 1])  # Starting with two 1s
            self.fib_step = 0
        elif self.system == 'Labouchere':
            self.labc_sequence = self.bet_amounts.copy()  # Sequence list
        elif self.system == '1-3-2-6':
            self.base_bet = self.bet_amounts
            self.sequence = [1, 3, 2, 6]
            self.current_step = 0
        elif self.system == "Oscars Grind":
            self.grind_goal = 1  
            self.current_grind = 0

    def define_sections(self):
        """
        Define the sections of the roulette wheel (mainly for 'Thirds').
        """
        if self.system == 'Thirds':
            numbers = [num for num in self.numbers if isinstance(num, int)]
            third = len(numbers) // 3
            first_third = numbers[:third]         
            second_third = numbers[third:2*third]
            third_third = numbers[2*third:]       
            return {
                'first': first_third,
                'second': second_third,
                'third': third_third
            }
        else:
            return {}

    def define_bet_coverage(self, bet_type):
        """
        Define which numbers (internally) we are 'covering' with the bet, 
        along with the payout ratio.

        :param bet_type: one of ['single', 'split', 'corner', 'line', 'dozen', 'even-chance']
        :return: (set_of_numbers, payout_multiplier)
        """
        # For demonstration, we assume the user always picks, e.g., 0 for single, 0-1 for split, etc.
        # The payout multipliers follow standard roulette rules:
        # single = 35:1, split = 17:1, street = 11:1, corner = 8:1, line = 5:1,
        # dozen = 2:1, column = 2:1, even-chance = 1:1
        # We'll implement just a subset for simplicity.

        if bet_type == 'single':
            return ({0}, 35)  # Bet on just '0'
        elif bet_type == 'split':
            return ({0, 1}, 17)  # A made-up split, e.g. 0-1
        elif bet_type == 'corner':
            return ({0, 1, 2, 3}, 8)  # A corner like 0-1-2-3 in some layouts
        elif bet_type == 'line':
            # A line is 6 numbers. We'll pretend it's [0,1,2,3,4,5]
            # though an American wheel would treat 0/00 differently.
            return (set(range(0,6)), 5)
        elif bet_type == 'dozen':
            # We'll treat 'first 12' as 1-12. 
            # If you actually want 0 in there, adapt it as needed.
            return (set(range(1,13)), 2)
        elif bet_type == 'even-chance':
            # We'll treat 'low numbers' as 1-18. 
            # (In actual roulette, you can do red/black, odd/even, etc.)
            return (set(range(1,19)), 1)
        else:
            # Default to single if input is unexpected
            return ({0}, 35)

    def spin_wheel(self):
        """Simulate spinning the roulette wheel."""
        return random.choice(self.numbers)

    def update_streak(self, net):
        """
        Update winning streak counters based on net result.
        """
        if net > 0:
            self.current_streak += 1
            self.current_streak_winnings += net
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
                self.longest_streak_winnings = self.current_streak_winnings
        else:
            self.current_streak = 0
            self.current_streak_winnings = 0.0

    def run(self):
        """
        Execute the simulation based on the selected betting system.

        :return: (history, final_balance, balance_over_time, total_wins, total_losses)
        """
        spin = 0
        while spin < self.max_spins and self.balance > 0:
            spin += 1

            # -- The main difference: If not using 'Thirds', we rely on self.is_win_coverage() 
            #    to see if we win based on the coverage in self.bet_numbers. 
            #    If using 'Thirds', we keep the old logic. 
            # 
            #    The code for each system remains the same, except we call self.is_win_coverage() 
            #    for our "place bet on coverage" scenario. 
            #
            #    For demonstration, all the systems below will call is_win_coverage() 
            #    (except Thirds which uses separate logic).
            
            if self.system == 'Thirds':
                # Keep the old code for Thirds
                bets = self.bet_amounts
                total_bet = bets.get('second', 0) + bets.get('third', 0)
                if self.balance < total_bet:
                    print(f"Spin {spin}: Insufficient balance to continue.")
                    break

                self.balance -= total_bet
                result = self.spin_wheel()
                self.spin_results.append(result)

                winning_section = None
                for section_name, numbers in self.sections.items():
                    if result in numbers:
                        winning_section = section_name
                        break

                if winning_section == 'first':
                    net = - (bets.get('second', 0) + bets.get('third', 0))
                elif winning_section == 'second':
                    payout = 2 * bets.get('second', 0)
                    net = payout - bets.get('third', 0)
                elif winning_section == 'third':
                    payout = 2 * bets.get('third', 0)
                    net = payout - bets.get('second', 0)
                else:
                    net = - (bets.get('second', 0) + bets.get('third', 0))

                self.balance += net
                self.history.append({
                    'spin': spin,
                    'bet': bets,
                    'result': result,
                    'winning_section': winning_section if winning_section else 'None (0 or 00)',
                    'net': net,
                    'balance': self.balance
                })

                if net > 0:
                    self.wins += 1
                    self.update_streak(net)
                    if self.prompt_after_win:
                        if not self.prompt_continue(spin):
                            break
                elif net < 0:
                    self.losses += 1
                    self.update_streak(0)
                else:
                    self.update_streak(0)

                self.balance_over_time.append(self.balance)
                continue

            # Otherwise, use normal system logic + coverage check
            current_bet = self.get_current_bet_amount()

            if self.balance < current_bet:
                print(f"Spin {spin}: Insufficient balance to continue.")
                break

            # Deduct the bet from the balance
            self.balance -= current_bet

            # Spin & check if coverage won
            result = self.spin_wheel()
            self.spin_results.append(result)
            won_this_spin = self.is_win_coverage(result)
            
            # Calculate net for this spin
            if won_this_spin:
                # If we 'win', the net is (payout * current_bet) - current_bet
                # e.g. for single number, 35 * bet - bet = 34 * bet net profit
                payout = self.bet_payout * current_bet
                spin_net = payout - current_bet
                self.balance += payout
                self.wins += 1

                self.history.append({
                    'spin': spin,
                    'bet': current_bet,
                    'result': result,
                    'outcome': 'Win',
                    'balance': self.balance
                })
                
                # Update streak
                self.update_streak(spin_net)

                # Let the system adjust the bet if necessary
                self.adjust_betting_system_after_spin(win=True)
                
                # If user wants to be prompted:
                if self.prompt_after_win:
                    if not self.prompt_continue(spin):
                        break
            else:
                # Lost the bet
                spin_net = - current_bet
                self.losses += 1

                self.history.append({
                    'spin': spin,
                    'bet': current_bet,
                    'result': result,
                    'outcome': 'Loss',
                    'balance': self.balance
                })

                # Update streak
                self.update_streak(0)

                # Let the system adjust if necessary
                self.adjust_betting_system_after_spin(win=False)

            self.balance_over_time.append(self.balance)
        
        return self.history, self.balance, self.balance_over_time, self.wins, self.losses

    def get_current_bet_amount(self):
        """
        Return the current bet size, depending on the system.
        For many systems, it's just self.current_bet.
        """
        if self.system == '1-3-2-6':
            # If using 1-3-2-6, we rely on the current step
            if hasattr(self, 'current_step') and self.current_step < len(self.sequence):
                return self.sequence[self.current_step] * self.base_bet
            else:
                return self.base_bet
        elif self.system == 'Oscars Grind' and hasattr(self, 'current_grind'):
            # If starting a new cycle vs in mid-cycle
            if self.current_grind == 0:
                return self.bet_amounts
            else:
                return self.current_bet
        else:
            # Default
            return self.current_bet

    def adjust_betting_system_after_spin(self, win):
        """
        Adjust bet size according to the chosen betting system 
        after each spin (unless the system is Thirds, handled separately).
        """
        if self.system == 'Martingale':
            if win:
                self.current_bet = self.bet_amounts
            else:
                self.current_bet *= 2

        elif self.system == 'Reverse Martingale':
            if win:
                self.current_bet *= 2
            else:
                self.current_bet = self.bet_amounts

        elif self.system == 'DAlembert':
            if win:
                self.current_bet = max(1, self.current_bet - 1)
            else:
                self.current_bet += 1

        elif self.system == 'Labouchere' and hasattr(self, 'labc_sequence'):
            if not self.labc_sequence:
                return  # All done
            if win:
                # We used bet = first + last
                if len(self.labc_sequence) == 1:
                    self.labc_sequence.pop(0)
                else:
                    self.labc_sequence.pop(0)
                    self.labc_sequence.pop(-1)
            else:
                lost_bet = self.labc_sequence[0] + self.labc_sequence[-1] if len(self.labc_sequence) > 1 else self.labc_sequence[0]
                self.labc_sequence.append(lost_bet)
            # Recalculate current_bet if sequence not empty
            if self.labc_sequence:
                if len(self.labc_sequence) == 1:
                    self.current_bet = self.labc_sequence[0]
                else:
                    self.current_bet = self.labc_sequence[0] + self.labc_sequence[-1]

        elif self.system == 'Paroli':
            if win:
                self.current_bet *= 2
            else:
                self.current_bet = self.bet_amounts

        elif self.system == "Oscars Grind" and hasattr(self, 'current_grind'):
            # If we won
            if win:
                self.current_grind += 1
                self.current_bet = self.bet_amounts
                if self.current_grind >= self.grind_goal:
                    print("Grind goal achieved!")
                    self.current_grind = 0
            else:
                # Typically no bet change after a loss in Oscar's Grind
                pass

        elif self.system == '1-3-2-6' and hasattr(self, 'current_step'):
            if win:
                self.current_step += 1
                if self.current_step >= len(self.sequence):
                    # Sequence complete, reset
                    self.current_step = 0
            else:
                self.current_step = 0

        elif self.system == 'Flat Betting':
            # No changes in bet
            pass
        else:
            # Unknown system or 'Thirds' (already handled)
            pass

    def is_win_coverage(self, spin_result):
        """
        Check if the spin result is within our chosen coverage set.
        For an American wheel with '00', we treat '00' as some unique item. 
        But if our coverage set has 0,1,2..., we just won't match '00' unless we explicitly add it.
        """
        return spin_result in self.bet_numbers

    def is_win(self, bet_number, spin_result):
        """
        Old method used for 'Thirds' approach or single number in original code.
        (We keep it for backward compatibility with the 'Thirds' system.)
        """
        return bet_number == spin_result

    def prompt_continue(self, spin):
        """
        Prompt the user to decide whether to continue gambling after a win.
        """
        print("\n--- Current Status ---")
        print(f"Spin Number: {spin}")
        print(f"Current Balance: ${self.balance:.2f}")
        print(f"Total Wins: {self.wins}")
        print(f"Total Losses: {self.losses}")
        if self.system in [
            'Martingale', 
            'Reverse Martingale', 
            'Fibonacci', 
            'DAlembert', 
            'Labouchere', 
            'Paroli', 
            "Oscars Grind", 
            "1-3-2-6"
        ]:
            if self.system == 'Labouchere':
                print(f"Current Sequence: {self.labc_sequence}")
            elif self.system == "1-3-2-6":
                print(f"Current Step in Sequence: {self.current_step + 1}")
                print(f"Current Bet: ${self.get_current_bet_amount():.2f}")
            elif self.system == "Oscars Grind":
                print(f"Current Grind: {self.current_grind}")
                print(f"Grind Goal: {self.grind_goal}")
            else:
                print(f"Current Bet: ${self.current_bet:.2f}")
            net = self.balance - self.initial_balance
            print(f"Net Profit/Loss: ${net:.2f}")
        elif self.system == 'Thirds':
            print(f"Current Bet on Second Third: ${self.bet_amounts.get('second', 0):.2f}")
            print(f"Current Bet on Third Third: ${self.bet_amounts.get('third', 0):.2f}")
            net = self.balance - self.initial_balance
            print(f"Net Profit/Loss: ${net:.2f}")
        elif self.system == 'Flat Betting':
            print(f"Current Bet: ${self.current_bet:.2f}")
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

    :return: 
       initial_balance, bet_amounts, system, max_spins, wheel_type, prompt_after_win, bet_type
    """
    print("Welcome to the Roulette Simulator!\n")

    # Additional choice: Bet Type
    # (single, split, corner, line, dozen, even-chance)
    bet_types = [
        ('single', 'Bet on a single number (pays 35:1)'),
        ('split', 'Bet on 2 numbers (pays 17:1)'),
        ('corner', 'Bet on 4 numbers (pays 8:1)'),
        ('line', 'Bet on 6 numbers (pays 5:1)'),
        ('dozen', 'Bet on 12 numbers (pays 2:1)'),
        ('even-chance', 'Bet on 18 numbers (pays 1:1)'),
    ]

    betting_systems = {
        'Martingale': 'Double your bet after every loss to recover previous losses.',
        'Reverse Martingale': 'Double your bet after every win to maximize streaks.',
        'Thirds': 'Bet on different thirds of the roulette wheel.',
        'Fibonacci': 'Follow the Fibonacci sequence for bet sizing.',
        'DAlembert': 'Increase your bet by one unit after a loss and decrease by one after a win.',
        'Labouchere': 'Use a sequence of numbers to determine bet amounts, adjusting after wins and losses.',
        'Paroli': 'Double your bet after every win to capitalize on winning streaks.',
        "Oscars Grind": 'Aim for small, steady profits by increasing your bet after wins.',
        "1-3-2-6": 'Follow a specific betting sequence to maximize profits during winning streaks.',
        'Flat Betting': 'Bet the same amount on every spin without changing your bet size.'
    }

    # Get balance
    while True:
        try:
            initial_balance = float(input("Enter your initial balance (e.g., 1000): $"))
            if initial_balance <= 0:
                print("Initial balance must be greater than 0.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")

    # Choose wheel type
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

    # Choose bet type (coverage)
    print("\nChoose your Bet Type (coverage on the table):")
    for idx, (b_type, desc) in enumerate(bet_types, 1):
        print(f"{idx}. {b_type} -> {desc}")
    while True:
        try:
            b_choice = int(input("Enter the number corresponding to your bet coverage choice: "))
            if 1 <= b_choice <= len(bet_types):
                bet_type = bet_types[b_choice - 1][0]
                break
            else:
                print(f"Please enter a number between 1 and {len(bet_types)}.")
        except ValueError:
            print("Please enter a valid number.")

    # Choose betting system
    systems = list(betting_systems.keys())
    print("\nChoose a betting system:")
    for idx, sys_name in enumerate(systems, 1):
        print(f"{idx}. {sys_name}: {betting_systems[sys_name]}")
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

    # If system == Thirds, we do that logic below. Otherwise standard:
    if system == 'Thirds':
        print("\nConfigure your Thirds Betting System:")
        print("You will specify bet amounts for the Second Third and Third Third.")
        print("First Third bet is $0 as per your strategy.")
        try:
            second_bet = float(input("Enter your bet amount for the Second Third (e.g., 5): $"))
            third_bet = float(input("Enter your bet amount for the Third Third (e.g., 10): $"))
            bet_amounts = {
                'first': 0,
                'second': second_bet,
                'third': third_bet
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
    elif system == 'Labouchere':
        print("\nConfigure your Labouchère Betting System:")
        sequence_input = input("Enter your desired sequence of numbers (e.g., 1,2,3): ")
        try:
            sequence = [int(num.strip()) for num in sequence_input.split(',')]
            if not sequence:
                raise ValueError
            bet_amounts = sequence
        except ValueError:
            print("Invalid input. Please enter a valid sequence of numbers.")
            sys.exit(1)
    elif system == '1-3-2-6':
        print("\nConfigure your 1-3-2-6 Betting System:")
        try:
            base_bet = float(input("Enter your base bet amount (e.g., 10): $"))
            if base_bet <= 0:
                print("Base bet must be greater than 0.")
                sys.exit(1)
            bet_amounts = base_bet
        except ValueError:
            print("Invalid input. Please enter a numeric value.")
            sys.exit(1)
    elif system == "Oscars Grind":
        print("\nConfigure your Oscar's Grind Betting System:")
        try:
            base_bet = float(input("Enter your base bet amount (e.g., 10): $"))
            if base_bet <= 0:
                print("Base bet must be greater than 0.")
                sys.exit(1)
            grind_goal = float(input("Enter your grind goal (profit target per cycle, e.g., 10): $"))
            bet_amounts = base_bet
        except ValueError:
            print("Invalid input. Please enter numeric values.")
            sys.exit(1)
    elif system == 'Flat Betting':
        print("\nConfigure your Flat Betting System:")
        try:
            bet_amount = float(input("Enter your fixed bet amount (e.g., 10): $"))
            if bet_amount <= 0:
                print("Bet amount must be greater than 0.")
                sys.exit(1)
            bet_amounts = bet_amount
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

    while True:
        try:
            max_spins = int(input("\nEnter the number of spins to simulate (e.g., 100): "))
            if max_spins <= 0:
                print("Number of spins must be greater than 0.")
                continue
            break
        except ValueError:
            print("Please enter a valid integer.")

    while True:
        choice = input("\nDo you want to be prompted after every win? (yes/no): ").strip().lower()
        if choice in ['yes', 'y']:
            prompt_after_win = True
            break
        elif choice in ['no', 'n']:
            prompt_after_win = False
            break
        else:
            print("Invalid choice. Please enter 'yes' or 'no'.")

    return (
        initial_balance, 
        bet_amounts, 
        system, 
        max_spins, 
        wheel_type, 
        prompt_after_win, 
        bet_type
    )

def plot_results(balance_over_time, wins, losses, system):
    """
    Plot Balance Over Time and Win/Loss Distribution.
    """
    fig, axs = plt.subplots(2, 1, figsize=(14, 10))

    axs[0].plot(balance_over_time, color='blue', linewidth=1)
    axs[0].set_title(f'Balance Over Time - {system} System')
    axs[0].set_xlabel('Spin Number')
    axs[0].set_ylabel('Balance ($)')
    axs[0].grid(True)

    # Mark initial balance
    axs[0].axhline(y=balance_over_time[0], color='green', linestyle='--', label='Initial Balance')
    axs[0].legend()

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
    (initial_balance, 
     bet_amounts, 
     system, 
     max_spins, 
     wheel_type, 
     prompt_after_win, 
     bet_type) = get_user_input()

    # Initialize the simulator
    simulator = RouletteSimulator(
        balance=initial_balance,
        bet_amounts=bet_amounts,
        system=system,
        max_spins=max_spins,
        wheel_type=wheel_type,
        prompt_after_win=prompt_after_win,
        bet_type=bet_type
    )

    # Run the simulation
    history, final_balance, balance_over_time, wins, losses = simulator.run()

    # Display Results
    print("\n--- Simulation Results ---")
    print(f"Betting System: {system}")
    print(f"Wheel Type: {wheel_type}")
    print(f"Bet Type (coverage): {bet_type}")
    print(f"Initial Balance: ${initial_balance}")
    print(f"Final Balance: ${final_balance}")
    print(f"Total Spins: {len(balance_over_time)}")
    print(f"Total Wins: {wins}")
    print(f"Total Losses: {losses}")
    net_pl = final_balance - initial_balance
    print(f"Net Profit/Loss: ${net_pl}")
    print(f"Longest Winning Streak: {simulator.longest_streak}")
    print(f"Amount Won in Longest Winning Streak: ${simulator.longest_streak_winnings:.2f}")

    # Plot the results
    plot_results(balance_over_time, wins, losses, system)

if __name__ == "__main__":
    main()
