go-curl
=======

my golang libcurl(curl) binding.

See more examples in ./examples/ directory!

LICENSE
-------

go-curl is licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0.html).

Current Development Status
--------------------------

 * currently stable
 * READ, WRITE, HEADER, PROGRESS function callback
 * a Multipart Form supports file uploading
 * Most curl_easy_setopt option
 * partly implement share & multi interface
 * new callback function prototype

How to Install
--------------

Make Sure You Have libcurl (and its develop headers, static/dynamic libs) installed!

    $ go get -u github.com/msva/go-curl

Sample Program
--------------

```go
package main

import (
    "fmt"
    curl "github.com/msva/go-curl"
)

func main() {
    easy := curl.EasyInit()
    defer easy.Cleanup()

    easy.Setopt(curl.OPT_URL, "http://www.baidu.com/")

    // make a callback function
    fooTest := func (buf []byte, userdata interface{}) bool {
        println("DEBUG: size=>", len(buf))
        println("DEBUG: content=>", string(buf))
        return true
    }

    easy.Setopt(curl.OPT_WRITEFUNCTION, fooTest)

    if err := easy.Perform(); err != nil {
        fmt.Printf("ERROR: %v\n", err)
    }
}
```
