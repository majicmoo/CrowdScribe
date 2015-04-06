(function($){
	var initLayout = function() {
        $('a.docGal').zoomimage({
            caption: false
        });
	};

	
	EYE.register(initLayout, 'init');
})(jQuery);