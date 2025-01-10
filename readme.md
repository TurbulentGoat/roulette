---

# Roulette Simulator

This is a Python-based Roulette Simulator that allows users to simulate various betting systems on both American and European roulette wheels. It provides options to choose different bet types and simulate up to 1000 spins, tracking balance and results over time.

## Features

- **Multiple Betting Systems**: Supports various betting systems like Martingale, Reverse Martingale, Fibonacci, DAlembert, Labouchere, Paroli, Oscar's Grind, 1-3-2-6, Flat Betting, and Thirds.
- **Bet Types**: Supports multiple bet types including single, split, corner, line, dozen, and even-chance.
- **Wheel Types**: Simulate spins on both American and European roulette wheels.
- **Balance Tracking**: Tracks the balance over time, winning and losing streaks.
- **User Prompts**: Option to prompt the user after every win to decide whether to continue gambling.

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/TurbulentGoat/roulette.git
   cd roulette
   ```

2. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

1. Run the simulator:
   ```sh
   python spin.py
   ```

2. Follow the prompts to configure your simulation:
   - Enter your initial balance.
   - Choose the type of roulette wheel (European or American).
   - Choose your bet type (single, split, corner, line, dozen, even-chance).
   - Choose a betting system.
   - Enter the number of spins to simulate.
   - Decide whether to be prompted after every win.

3. The simulation will run and display results, including:
   - Betting System
   - Wheel Type
   - Bet Type
   - Initial Balance
   - Final Balance
   - Total Spins
   - Total Wins
   - Total Losses
   - Net Profit/Loss
   - Longest Winning Streak
   - Amount Won in Longest Winning Streak

4. A plot of the balance over time and win/loss distribution will be displayed.

## Example

```sh
Welcome to the Roulette Simulator!

Enter your initial balance (e.g., 1000): $1000
Choose the type of roulette wheel:
1. European
2. American
Enter the number corresponding to your choice: 1
Choose your Bet Type (coverage on the table):
1. single -> Bet on a single number (pays 35:1)
2. split -> Bet on 2 numbers (pays 17:1)
3. corner -> Bet on 4 numbers (pays 8:1)
4. line -> Bet on 6 numbers (pays 5:1)
5. dozen -> Bet on 12 numbers (pays 2:1)
6. even-chance -> Bet on 18 numbers (pays 1:1)
Enter the number corresponding to your bet coverage choice: 1
Choose a betting system:
1. Martingale: Double your bet after every loss to recover previous losses.
...
Enter the number corresponding to your choice: 1
Enter your initial bet amount (e.g., 10): $10
Enter the number of spins to simulate (e.g., 100): 100
Do you want to be prompted after every win? (yes/no): no

--- Simulation Results ---
Betting System: Martingale
Wheel Type: European
Bet Type (coverage): single
Initial Balance: $1000
Final Balance: $800
Total Spins: 100
Total Wins: 45
Total Losses: 55
Net Profit/Loss: -$200
Longest Winning Streak: 5
Amount Won in Longest Winning Streak: $170.00
```

## Contributing

Contributions are welcome! Please open an issue to discuss your ideas or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by the various betting systems and the mathematical curiosity around them.
- Thanks to the contributors and the open-source community for their valuable inputs.

---

Feel free to modify this README to better suit your project's needs.
