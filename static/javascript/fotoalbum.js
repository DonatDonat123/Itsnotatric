var left_panel = $('.left-panel')
var show_house = $('.show-house')
var img_active = $('.img-active')
var img_panel = $('.img-panel')
var panel_col = $('.panel-col')
var panel_toggled = false
var winWidth=$(window).width();
var winHeight=$(window).height();

var columnWidth = panel_col.width();
var maxColumnWidth = (3.0/4.0) * columnWidth;

show_house.css(
    {
    "width": winWidth,
    "height": winHeight,
    "max-width": winWidth,
    "max-height": winHeight
    });

panel_col.css(
{
    "max-height": maxColumnWidth
})
center_main_img()

function toggle_left_panel(){
    if (panel_toggled){
        left_panel.animate({left: '0px'});
        panel_toggled = false;
        img_active.animate({
            opacity: '0.4'
        },1000);
    }
    else{
        left_panel.animate({left: '-500px'});
        panel_toggled = true;
        img_active.animate({
            opacity: '1.0'
        },1000);
    }
}

function center_main_img(){
    new_margin_left = (winWidth-img_active.outerWidth())/2
    img_active.css(
    {
    "margin-left": new_margin_left
    })
}

function make_img_active(img_clicked){
    img_active.attr("src", img_clicked.attr("src"))
    center_main_img()
}

img_panel.on('click', function(e){
  e.preventDefault()
  var $this=$(this);
  make_img_active($this)
  });

img_active.on('click', function(e){
  e.preventDefault()
  toggle_left_panel()
});