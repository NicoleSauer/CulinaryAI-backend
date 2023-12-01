const express = require("express");
const app = express();

let ingredients = [
  {
    id: 1,
    name: "Karotten",
  },
  {
    id: 2,
    name: "Sahne",
  },
  {
    id: 3,
    name: "Brokkoli",
  },
];

app.get("/", (request, response) => {
  response.send("<h1>CulinaryAI</h1>");
});

app.get("/api/ing", (request, response) => {
  response.json(ingredients);
});

const PORT = 5000;

app.listen(PORT, () => {
  console.log(`Server running on 127.0.0.1:${PORT}`);
});
