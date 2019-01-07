require('babel-register')({
    presets: ['es2015', 'es2016', 'es2017', 'stage-0'],
    plugins: ['transform-runtime'],
});
require('pretty-error').start();

require('./src/app');
