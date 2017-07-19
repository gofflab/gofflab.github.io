var tl = new TimelineMax({ repeat: -1 });

//Helper Utilities
var pauseBtn = document.getElementById("pause");

//tl.staggerTo(".circle", 1.5, {x:640, repeat:-1, repeatDelay:0.5, force3D:true, ease:SlowMo.ease.config(0.2, 0.5)}, 0.15)

pauseBtn.onclick = function() {
  tl.paused(!tl.paused());
  //pauseBtn.innerHTML = tl.paused() ? "play" : "pause";
}

//Canvas settings
var xMax = 1000;
var yMax = 800;
var noise=75;

var startCenter = {
  x: 100,
  y:yMax-100
};

var typeSize=100;
var startSize=50;

// RANDOM NUMBER MIN MAX - https://gist.github.com/timohausmann/4997906
var randMinMax = function(t, n, a) {
  var r = t + Math.random() * (n - t)
  return a && (r = Math.round(r)), r
}
var paths = {

path1: [
    { opacity: 1, x: xMax * 0.25, y: yMax * 0.35, fill: '#0c0' },
    { opacity: 1, x:  function() { return (xMax * 0.65)+Math.cos(Math.random() * Math.PI * 2) * (Math.random() * noise);}, y: function() { return (yMax * 0.50)+Math.cos(Math.random() * Math.PI * 2) * (Math.random() * noise);}, fill: '#c00' },
    { opacity: 0, x: function() { return (xMax-100)-Math.cos(Math.random() * Math.PI * 2) * (Math.random() * noise);}, y: function() { return (0)+Math.cos(Math.random() * Math.PI * 2) * (Math.random() * noise);}, fill: '#c00' },
  ],
path2:[
    { opacity: 1, x: xMax * 0.25, y: yMax * 0.35, fill: '#0c0' },
    { opacity: 1, x:  function() { return (xMax * 0.75)+Math.cos(Math.random() * Math.PI * 2) * (Math.random() * noise);}, y: function() { return (yMax * 0.50)+Math.cos(Math.random() * Math.PI * 2) * (Math.random() * noise);}, fill: '#c0c' },
    { opacity: 0, x: function() { return (xMax-100)+Math.cos(Math.random() * Math.PI * 2) * (Math.random() * noise);}, y: function() { return (400)+Math.cos(Math.random() * Math.PI * 2) * (Math.random() * noise);}, fill: '#00f' },
  ],
path3:[
    { opacity: 1, x: xMax * 0.25, y: yMax * 0.35, fill: '#0c0' },
    { opacity: 1, x:  function() { return (xMax * 0.50)+Math.cos(Math.random() * Math.PI * 2) * (Math.random() * noise);}, y: function() { return (yMax * 0.70)+Math.cos(Math.random() * Math.PI * 2) * (Math.random() * noise);}, fill: '#c00' },
    { opacity: 0, x: function() { return (xMax-100)+Math.cos(Math.random() * Math.PI * 2) * (Math.random() * noise);}, y: function() { return (750)+Math.cos(Math.random() * Math.PI * 2) * (Math.random() * noise);}, fill: '#ff0' },
  ],
path4:[
    { opacity: 1, x: xMax * 0.20, y: yMax * 0.30, fill: '#0c0' },
    { opacity: 1, x:  function() { return (xMax * 0.20)+Math.cos(Math.random() * Math.PI * 2) * (Math.random() * noise);}, y: function() { return (yMax * 0.40)+Math.cos(Math.random() * Math.PI * 2) * (Math.random() * noise);}, fill: '#dad' },
    { opacity: 1, x:  function() { return (xMax * 0.20)+Math.cos(Math.random() * Math.PI * 2) * (Math.random() * noise);}, y: function() { return (yMax * 0.35)+Math.cos(Math.random() * Math.PI * 2) * (Math.random() * noise);}, fill: '#858' },
    { opacity: 1, x:  function() { return (xMax * 0.20)+Math.cos(Math.random() * Math.PI * 2) * (Math.random() * noise);}, y: function() { return (yMax * 0.40)+Math.cos(Math.random() * Math.PI * 2) * (Math.random() * noise);}, fill: '#fcf' },
    { opacity: 1, x:  function() { return (xMax * 0.20)+Math.cos(Math.random() * Math.PI * 2) * (Math.random() * noise);}, y: function() { return (yMax * 0.35)+Math.cos(Math.random() * Math.PI * 2) * (Math.random() * noise);}, fill: '#858' },
    { opacity: 0, x: function() { return (50)+Math.cos(Math.random() * Math.PI * 2) * (Math.random() * noise);}, y: function() { return (0)+Math.cos(Math.random() * Math.PI * 2) * (Math.random() * noise);}, fill: '#b8b' },
  ]

};

var path1 = [
    { opacity: 1, x: xMax * 0.25, y: yMax * 0.25, fill: '#0c0' },
    { opacity: 1, x: xMax * 0.75, y: yMax * 0.50, fill: '#c00' },
    { opacity: 1, x: xMax-100, y: 100, fill: '#c0c' },
  ];


var path2 = [
    { opacity: 1, x: xMax * 0.25, y: yMax * 0.25, fill: '#0c0' },
    { opacity: 1, x: xMax * 0.75, y: yMax * 0.50, fill: '#c00' },
    { opacity: 1, x: xMax-100, y: 600, fill: '#ff0' },
  ];

// Returns one single Cloud by duplicating the existing Cloud element
var createCloud = function(element) {
  var newElement = element.cloneNode(true);
  element.parentNode.insertBefore(newElement, element.nextSibling);
  return newElement;
};

//Random motion of cells within radius
var randMotion = function (clouds,noise) {
    tl.staggerTo(clouds, 1, {
      cycle:{
        x:function() { return Math.random() * 200; },
        y:function() { return Math.random() * 200; },
      // x: function() { 

      //               return Math.cos(Math.random() * Math.PI * 2) * (Math.random() * noise);
      //             }, 
      // y: function() {
      //               return Math.sin(Math.random() * Math.PI * 2) * (Math.random() * noise);
      //       }, 
      ease: Power0.easeInOut,
    },
    repeat: -1,
    postion: "Start+=1"
    //onComplete: randMotion(this,noise),
  });

};


// Initial placement of all clouds objects
var placeClouds = function(clouds) {
  TweenMax.staggerTo(clouds, 0, {
    cycle: {
      //x: function() { return startCenter.x + randMinMax(-startSize, startSize); },
      //y: function() { return startCenter.y + randMinMax(-startSize, startSize); },
      x: function() { 

                    return startCenter.x + Math.cos(Math.random() * Math.PI * 2) * (Math.random() * noise);
                  }, 
      y: function() {
                    return startCenter.y + Math.sin(Math.random() * Math.PI * 2) * (Math.random() * noise);
            }, 
      //x: 10,
      //y: 12,
      scale: function() { return randMinMax(0.8, 1.2); },
    },
    opacity: 0
  }, 0);
};

// Addition of all cloud elements into main TimelineMax instance
var diffPath = function(clouds,curpath) {
  tl.staggerTo(clouds, 8, {
    cycle: {
      //x: function() { return randMinMax(0, xMax); },
      //y: function() { return randMinMax(0, yMax); },
      scale: function() { return randMinMax(0.6, 2); },
    },
    bezier: { values: curpath, type: 'soft', curviness: 0.8 },
    ease: Power0.easeInOut,

  }, 0.1,"Start");
};

// Addition of all cloud elements into main TimelineMax instance
// var tweenNoise = function(clouds) {
//   tl.staggerTo(clouds, 4, {
//     cycle: {
//       x: function() { return clouds[index].x+randMinMax(-100,100); },
//       y: function() { return clouds[index].y+randMinMax(-100,100); },
//       onComplete: tweenNoise,
//     },
//     ease: Power0.easeInOut
//   }, 0.1, "Next");
// };

var clouds = function(cloud, numClouds,curpath) {
  var clouds;
  var element = document.querySelector(cloud);
  for (var i = 0; i < numClouds; i++) { createCloud(element); }
  clouds = document.querySelectorAll(cloud);
  //console.log(clouds)
  placeClouds(clouds);
  diffPath(clouds,curpath);
  //randMotion(clouds,noise);
};

clouds('.dust', 200, paths.path1);
clouds('.dust2', 200, paths.path2);
clouds('.dust3', 200, paths.path3);
clouds('.dust4', 200, paths.path4);