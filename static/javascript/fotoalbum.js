var left_panel = $('.left-panel')
var panel_toggled = false
function toggle_left_panel(){
    if (panel_toggled){
        $('.left-panel').animate({left: '0px'});
        panel_toggled = false;
    }
    else{
        $('.left-panel').animate({left: '-600px'});
        panel_toggled = true;
    }
}

$(document).click(function() {
 toggle_left_panel()
});