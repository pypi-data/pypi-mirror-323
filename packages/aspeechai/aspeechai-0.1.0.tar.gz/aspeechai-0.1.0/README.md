# ASpeechAI's Python SDK

This project is aimed at providing a Python SDK for our A-SpeechAI API. It allows developers to easily integrate the A-SpeechAI capabilities into their Python applications to transcribe and understand audio

## Installation

Before starting, you need to set the API key. If you don't have one yet, [sign up for one](https://platform.a-speechai.com/login)!

To install the A-SpeechAI Python SDK, simply run the following command:

```
pip install aspeechai
```

## Usage

To use the A-SpeechAI Python SDK, you need to import the `Transcriber` and `Client` classes from the `aspeechai` module. Here's an example of how to use it:

```python
from aspeechai import Transcriber as tr, Client

# Create an instance of the A-SpeechAI class

TOKEN="af_zf......."
EMAIL="example@example.com"

client = Client(token=TOKEN,
                email=EMAIL)

# Call the desired API method
transcriber = tr(client=client)
response = transcriber.transcribe(data="audio_file",
                                language_code="fon",
                                )
print(response)
```

## Documentation

For detailed documentation on how to use the A-SpeechAI Python SDK, please refer to the [official documentation](https://platform.a-speechai.com/).

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request on the [GitHub repository](https://github.com/A-speechAI/aspeechai-python-sdk).

## License

This project is licensed under the [MIT License](LICENSE).
