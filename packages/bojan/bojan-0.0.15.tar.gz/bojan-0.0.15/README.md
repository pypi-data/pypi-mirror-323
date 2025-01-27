# Bojan Library

BojanConsole is a Python library designed to enhance console logging with various message types and color-coded outputs.

## Installation

To install Bojan simply run

```bash
pip install bojan
```

## Syntax Highlight

A [VS Code extension](https://github.com/daniilgrydin/bojan-vscode-highlighter) is available to highlight the .bojan and .bjn log files.

## Usage

### BojanConsole Class

#### Initialization

```python
from bojan import BojanConsole

console = BojanConsole(printing=True)
```
> Note that `printing` decides whether the instance will print to terminal or just store logs for later use. 

#### Logging Messages

- **Info Message**:
    ```python
    console.print("This is an info message.", identifier="🗣️", depth=0)
    ```
    output:
    ```
    🗣️ This is an info message.
    ```

- **Debug Message**:
    ```python
    console.debug("This is a debug message.")
    ```
    output:
    ```
    💬 This is a debug message.
    ```

- **Error Message**:
    ```python
    console.error("This is an error message.")
    ```
    output:
    ```
    ❌ This is an error message.
    ```

- **Success Message**:
    ```python
    console.success("This is a success message.")
    ```
    output:
    ```
    ✅ This is a success message.
    ```

- **Warning Message**:
    ```python
    console.warning("This is a warning message.")
    ```
    output:
    ```
    ⚠️ This is a debug message.
    ```

#### Printing Dictionaries

```python
sample_dict = {"key1": "value1", "key2": {"subkey1": "subvalue1"}}
console.dictionary(sample_dict)
```
output:
```
🏰 key1
    🛖 value1
    🛖 subkey1
        🌲 subvalue 1
```
> The emojis use following hierarchy: 🏰 🛖 🌲 🐦 🐛 🧬

#### Depth

The depth parameter of all logging functions determines how nested the message is by inserting a corresponding amount of tabs.

```python
console.print("Message!", depth=0)
console.print("Nested message!", depth=1)
console.error("Nested error message!", depth=1)
```

output:

```
🕸️ Message!
    🕸️ Nested message!
    ❌ Nested error message!
```

#### Saving Logs

```python
console.save("logfile.bojan")
```

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.