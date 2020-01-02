// Based on https://codepen.io/arickle/pen/XKjMZY

const makeItRain = () => {
  const rain = document.querySelector('.rain');
  //clear out everything
  while (rain.firstChild) {
    rain.removeChild(myNode.firstChild);
  }

  let increment = 0;
  let drops = "";
  let backDrops = "";

  while (increment < 100) {
    //couple random numbers to use for various randomizations
    //random number between 98 and 1
    let randoHundo = (Math.floor(Math.random() * (98 - 1 + 1) + 1));
    //random number between 5 and 2
    let randoFiver = (Math.floor(Math.random() * (5 - 2 + 1) + 2));
    //increment
    increment += randoFiver;
    //add in a new raindrop with various randomizations to certain CSS properties
    drops += `<div class="drop" style="left: ${increment}%;
        bottom: ${(randoFiver + randoFiver - 1 + 100)}%;
        animation-delay: 0.${randoHundo}s; 
        animation-duration: 0.5${randoHundo}s;">
        <div class="stem" style="animation-delay: 0.${randoHundo}s; 
          animation-duration: 0.5${randoHundo}s;">
        </div>
      </div>`;
    backDrops += `<div class="drop" style="right: ${increment}%;
        bottom: ${(randoFiver + randoFiver - 1 + 100)}%;
        animation-delay: 0.${randoHundo}s; 
        animation-duration: 0.5${randoHundo}s;">
        <div class="stem" style="animation-delay: 0.${randoHundo}s; 
          animation-duration: 0.5${randoHundo}s;">
        </div>
      </div>`;
  }

  document.querySelector('.rain.front-row').innerHTML += drops;
  document.querySelector('.rain.back-row').innerHTML += backDrops;
}

makeItRain();