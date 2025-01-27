## Judobase API Client
This is a async Python client for the Judobase API.

## Installation

To install the package, use pip:

```bash
pip install judobase
```

## Usage

Here is an example of how to use the Judobase API client:

```python
import asyncio

from judobase import JudoBase

async def main():
    async with JudoBase() as api:
        contests = await api.get_all_contests()
        print(len(contests))

asyncio.run(main())
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
