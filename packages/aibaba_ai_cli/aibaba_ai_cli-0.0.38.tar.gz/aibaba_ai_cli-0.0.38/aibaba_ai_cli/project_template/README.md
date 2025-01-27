# __app_name__

## Installation

Install the Aibaba AI CLI if you haven't yet

```bash
pip install -U aibaba_ai_cli
```

## Adding packages

```bash
# adding packages from 
# https://github.com/aibaba-ai/aibaba-ai/tree/master/templates
aibaba_ai_cli app add $PROJECT_NAME

# adding custom GitHub repo packages
aibaba_ai_cli app add --repo $OWNER/$REPO
# or with whole git string (supports other git providers):
# langchain app add git+https://github.com/hwchase17/chain-of-verification

# with a custom api mount point (defaults to `/{package_name}`)
aibaba_ai_cli app add $PROJECT_NAME --api_path=/my/custom/path/rag
```

Note: you remove packages by their api path

```bash
aibaba_ai_cli app remove my/custom/path/rag
```


## Launch aibaba_ai

```bash
aibaba_ai_cli serve
```

## Running in Docker

This project folder includes a Dockerfile that allows you to easily build and host your aibaba_ai app.

### Building the Image

To build the image, you simply:

```shell
docker build . -t my-aibaba_ai-app
```

If you tag your image with something other than `my-aibaba_ai-app`,
note it for use in the next step.

### Running the Image Locally

To run the image, you'll need to include any environment variables
necessary for your application.

In the below example, we inject the `OPENAI_API_KEY` environment
variable with the value set in my local environment
(`$OPENAI_API_KEY`)

We also expose port 8080 with the `-p 8080:8080` option.

```shell
docker run -e OPENAI_API_KEY=$OPENAI_API_KEY -p 8080:8080 my-aibaba_ai-app
```
