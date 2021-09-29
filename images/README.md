# Demo image

The build script is parameterized around the `SERVER_BASE` and `WEB_BASE`. It outputs two tagged images, `deephaven/custom-server` and `deephaven/custom-web`.

For example:

```sh
SERVER_BASE=deephaven/grpc-api:local-build WEB_BASE=deephaven/web:local-build ./build.sh
```
