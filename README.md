# Chrome MCP Server

We are building a server that will be used to interact with Chrome. There are two main goals to this project:

1. Providing an MCP implementation that does not rely on the MCP library provided by Anthropic.
2. Creating a Chrome MCP server that we can use in Cursor to take screenshots of a page and validate the implementation.

> [!NOTE]
> This is not a reference implementation of the MCP protocol, this was a learning exercise to better understand the protocol and how it works.

A more robust implementation is located in the `app` folder.

## Demo implementation

This is a simple implementation of the [MCP protocol](https://spec.modelcontextprotocol.io/specification/2024-11-05/), as such we
have not implemented all the features of the MCP protocol. We focused on building a first set of features that we can use to
get a functioning implementation.

It can be run by executing the following command:

```bash
uv run uvicorn demo_implementation.main:app --reload
```

and then tested by running the MCP inspector:

```bash
npx @modelcontextprotocol/inspector node build/index.js
```

Once in the inspector, you can connect to our server using the URL: `http://0.0.0.0:8000`

### How it works

There are two main components to the demo implementation:

1. An event stream that is used to send messages from the server to the client.
2. A POST endpoint that is used to send messages from the client to the server.

The implementation focuses on implementing the initialization process and tools. We did not look at implementatinf other features.
The initialization process is done in three parts with:

1. Initial call to the `/sse` endpoint to get the session URI.
2. Client sends a `initialize` message to the server that responds with the functionality supported by the server.
3. Client sends a `notifications/initialized` message to the server to notify that the initialization is complete.

Once this is implemented, the client can start sending messages to the server to use the tools.

### Limitations of the demo implementation

The demo implementation has a number of limitations including lack of error handling, no adequate cleanup of the sessions and more.
We added more robust implementation in `app/main.py` that relies on the MCP Python SDK.

## Robust implementation

The more robust implementation relies on the MCP Python SDK to handle the connection and the messages.

This implementation is located in `app/main.py`.

### How it works

This is much simpler as all we need to do is define the three functions to be used as tools. Once these are defined, we can test
the implementation by running the `app/main.py` file:

```bash
# Start the server
mcp run app/main.py --transport sse
```

and then in another terminal we can start the MCP inspector:

```bash
npx @modelcontextprotocol/inspector node build/index.js
```
