const gulp = require("gulp");
const concat = require("gulp-concat");
const cleanCSS = require("gulp-clean-css");

gulp.task("styles", function () {
  return gulp
    .src("static/style/*.css") // Adjust the path to where your CSS files are
    .pipe(concat("bundle.css")) // This will concatenate all CSS files into bundle.css
    .pipe(cleanCSS({ compatibility: "ie8" })) // Minify the CSS
    .pipe(gulp.dest("static/style/")); // Adjust the destination folder
});
