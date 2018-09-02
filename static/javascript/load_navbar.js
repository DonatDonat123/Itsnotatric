$(function(){
    //$nb = load("./static/templates/navbar.html")
  var me = {};
  me.avatar = "./static/fotos/dd_profile.png";
  nb = $(".navbarspace")
  nb.html('<div class="avatar_user"><img class="img-left" style="width:100%;" src="'+ me.avatar +'" /></div>');
  nb.load("./static/templates/interactive.html");
  console.log(nb.html())
  });

