# Server

When your are starting the server for the first time, you will need to install the required packages. Bur first we need to make sure Node.js is installed.

You can test this by running the following command:

```
node -v
```

If you see a version number, you have Node.js installed. If not, you can download it [here](https://nodejs.org/en/download/). </br>
After installing Node.js, you should be able to run the command above and see a version number.

Now, you can install the required packages. Please make sure you are in the **server** directory! </br>
If so, try running:

```
npm install
```

Then, to start the server (while being in the **server** directory), run the following command:

```
npm run dev
```

It is `npm run dev` instead of the usual `npm run start` because we are using [nodemon](https://www.npmjs.com/package/nodemon) to automatically restart the server when we make changes to the code. That´s pretty useful when developing.

If you want to know what is happening, you can take a look at the `package.json` file under the `scripts` section. There you can see that `npm run dev` is just an alias for `nodemon index.js`, which is using the nodemon package to run the `index.js` file, which then starts the server.

### The server should now be running. You can check it by visiting your [localhost](127.0.0.1:5000) on port 5000.
