//
// Copyright 2023 Google. This software is provided as-is, without warranty
// or representation for any use or purpose. Your use of it is subject
// to your agreement with Google.
//
package main

import (
    "context"
    "fmt"
    "io"
    "time"
    "os"
    "log"
    "bufio"
    "cloud.google.com/go/storage"
  	"google.golang.org/api/impersonate"
   	"google.golang.org/api/option"
)

// generateV4GetObjectSignedURL generates object signed URL with PUT method.
func generateV4PutObjectSignedURL(w io.Writer, bucket, object string) (string, error) {
    // bucket := "bucket-name"
    // object := "object-name"

    ctx := context.Background()
    // impersonate service accouhnt
    // Base credentials sourced from ADC or provided client options.
    ts, err := impersonate.CredentialsTokenSource(ctx, impersonate.CredentialsConfig{
    	TargetPrincipal: "signurl-service-account@ashires-joonix-test-1.iam.gserviceaccount.com",
    	Scopes:          []string{"https://www.googleapis.com/auth/cloud-platform"},
    	// Optionally supply delegates.
    	// Delegates: []string{"bar@project-id.iam.gserviceaccount.com"},
    })
    if err != nil {
	   log.Fatal(err)
    }
    // get storage client using impersonated credentaiisl
    client, err := storage.NewClient(ctx, option.WithTokenSource(ts))
    if err != nil {
        return "", fmt.Errorf("storage.NewClient: %v", err)
    }
    defer client.Close()

    // Signing a URL requires credentials authorized to sign a URL. You can pass
    // these in through SignedURLOptions with one of the following options:
    //    a. a Google service account private key, obtainable from the Google Developers Console
    //    b. a Google Access ID with iam.serviceAccounts.signBlob permissions
    //    c. a SignBytes function implementing custom signing.
    // In this example, none of these options are used, which means the SignedURL
    // function attempts to use the same authentication that was used to instantiate
    // the Storage client. This authentication must include a private key or have
    // iam.serviceAccounts.signBlob permissions.
    opts := &storage.SignedURLOptions{
        Scheme: storage.SigningSchemeV4,
        Method: "PUT",
        Headers: []string{
            "Content-Type:application/octet-stream",
        },
        Expires: time.Now().Add(12 * time.Hour),
        GoogleAccessID: "signurl-service-account@ashires-joonix-test-1.iam.gserviceaccount.com",
    }

    u, err := client.Bucket(bucket).SignedURL(object, opts)
    if err != nil {
        return "", fmt.Errorf("Bucket(%q).SignedURL: %v", bucket, err)
    }

    fmt.Printf("Generated PUT signed URL:")
    fmt.Printf("%q\n", u)
    fmt.Printf("You can use this URL with any user agent, for example:")
    fmt.Printf("curl -X PUT -H 'Content-Type: application/octet-stream' --upload-file my-file %q\n", u)
    return u, nil
}

func main() {
    fmt.Println("help text goes here")
    fmt.Printf("args: %s", os.Args)
    var gcs_bucket = os.Args[1]
    var gcs_object = os.Args[2]
    var out = os.Stdout
    var writer = bufio.NewWriter(out)
    var signed_url, err = generateV4PutObjectSignedURL(writer, gcs_bucket, gcs_object)
    if err != nil {
      fmt.Println(signed_url)
    }
    fmt.Println(err)
}
