# CLI Helper Tool

A CLI helper tool that helps with day-to-day commands and automates software development tasks. This tool provides configuration management and a CLI-friendly cyborg tool for other tasks.

## Installation

To install this tool via **pip**, run:

```bash
pip install cli
```

Alternatively, if you are using Poetry, run:

```bash
poetry install
```

## Usage

After installing the package, you can access the command line tool using the `pilot` command.

### Commands

This tool provides the following commands:

### `config` - Configuration options

The `config` command allows you to manage configuration key-value pairs.

#### Subcommands

- **`create`**: Set a configuration key-value pair.

  Usage:
  ```bash
  pilot config create <key=value>
  ```
  Example:
  ```bash
  pilot config create api_key=12345
  ```

- **`read`**: Read a configuration value by key or print all key-value pairs.

  Usage:
  ```bash
  pilot config read <key>
  ```

  If the `key` is omitted, all key-value pairs will be displayed:
  ```bash
  pilot config read
  ```

  Example:
  ```bash
  pilot config read api_key
  ```

- **`remove`**: Remove a configuration value by key.

  Usage:
  ```bash
  pilot config remove <key>
  ```
  Example:
  ```bash
  pilot config remove api_key
  ```

### `cyborg` - A CLI friendly cyborg tool

The `cyborg` command provides a simple cyborg tool to run a specific CLI-friendly app.

#### Subcommands

- **`run`**: Run the Cyborg app.

  Usage:
  ```bash
  pilot cyborg run
  ```

## Example Usage

### 1. **Set a configuration key-value pair**:
```bash
pilot config create api_key=12345
```

### 2. **Read a configuration key**:
```bash
pilot config read api_key
```

### 3. **Read all configuration key-value pairs**:
```bash
pilot config read
```

### 4. **Remove a configuration key**:
```bash
pilot config remove api_key
```

### 5. **Run the Cyborg app**:
```bash
pilot cyborg run
```

## Dependencies

This CLI tool relies on the following packages:
- `click`
- `colorama`
- `textual`
- `ollama`

You can manage and install the dependencies using **Poetry** or **pip**.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

### Key Updates:
1. **Changed Command Name to `pilot`**: Since your tool is published as `cli` but should be executed with the `pilot` command, I’ve updated all references of the command to `pilot`.
2. **Clarified Installation**: Both `pip` and `Poetry` installation methods are included for flexibility.

---

This README should now correctly reflect your tool's installation and usage instructions with the proper command (`pilot`).