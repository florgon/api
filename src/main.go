package main

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

func index(c *gin.Context) {
	// TODO: Encapsulate struct / response logic.
	var message struct {
		Status  int    `json:"status"`
		Version string `json:"v"`
		Payload struct {
			Methods []string `json:"methods"`
		} `json:"success"`
	}

	message.Status = http.StatusOK
	message.Version = "v0.1 DEV"
	message.Payload.Methods = []string{"/"}
	c.JSON(message.Status, message)
}

func main() {
	r := gin.Default()

	r.GET("/", index)
	r.Run()
}
