var webpack = require("webpack");
var path = require("path");
 
module.exports = {
  module: {
    loaders: [
      {
        loader: "babel-loader",
        // Skip any files outside of your project's `src` directory
        include: [
          path.resolve(__dirname, "project/static/scripts/jsx/"),
        ],
        // Only run `.js` and `.jsx` files through Babel
        test: /\.jsx?$/,
        // Options to configure babel wisth
        query: {
          plugins: ['transform-runtime'],
          presets: ['es2015', 'react', 'stage-2'],
        }
      }
    ]
  },
  output: {
    path: path.resolve(__dirname, "project/static/scripts/js/"),
    filename: '[name].bundle.js'
  },
  entry: {
      workspace: './project/static/scripts/jsx/containers/workspace.js'
  }
};