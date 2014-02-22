$(function() {
    $('.jcarousel').jcarousel({
    	wrap: 'circular'
    });
    $('.jcarousel').jcarouselAutoscroll({
        interval: 3000,
        target: '+=1',
        autostart: true,
        scroll: 1
    });
});