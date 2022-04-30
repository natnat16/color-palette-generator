function copyHex(cId) {
  // function to copy hex code to clipboard
  var code = document.getElementById('hex-' + cId);
  var rect = document.getElementById('rect-' + cId);
  navigator.clipboard.writeText(code.innerText);
  rect.textContent='copied!'
  rect.style.color = 'transparent';
}

function checkCalculation() {
  // inrteacting with flask, checking when palette calculation is done
  fetch('/check_calc') 
    .then(function(response) {
      if (response.redirected) {
       console.log('done')
       window.location.href = response.url;
      } else {
      console.log('calculating')
      }
    }) 
}

function checkForPalette() {
  // Set checkCalculation function to run every 3s until calculation done.
  const cInterval = setInterval(checkCalculation, 3000);
}
