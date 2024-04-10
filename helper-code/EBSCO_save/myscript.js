$(document).ready(function() {
    save();
    /* var autoLink =  $('a[id$="_lnkNext"]');
    autoLink.click(); */
    window.scrollTo(0, document.body.scrollHeight);
    });

function save() {
  var htmlContent = $('html').html();
  var bl = new Blob([htmlContent], {type: "text/html"});
  var a = document.createElement("a");
  a.href = URL.createObjectURL(bl);
  a.download = Math.floor(Date.now() / 1000) + ".html";
  a.hidden = true;
  document.body.appendChild(a);
  a.innerHTML = "something random - nobody will see this, it doesn't matter what you put here";
  a.click();
}