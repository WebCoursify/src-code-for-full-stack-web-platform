(function(window, $){

	var App = {}

	function setFollow(userId, toFollow, callback){
		var url;
		if(toFollow)
			url = '/api/user/follow';
		else
			url = '/api/user/unfollow';

		$.ajax({
			type: 'POST',
			url: url,
			data: {'target_user_id': userId},
			dataType: 'json',
			success: function(res){
				if(res.error)
					callback(res.error);
				else
					callback(null, res);
			},
			error: function(e){
				callback(e);
			}
		});
	}

	App.initFollowButtons = function(toCenter){
		function setText(elem){
			var classFollowed = 'btn-default', classNotFollowed = 'btn-success';

			if(elem.data('followed') == 1){
				elem.html(elem.data('text-followed')).addClass(classFollowed).removeClass(classNotFollowed);
			}else{
				elem.html(elem.data('text-to-follow')).addClass(classNotFollowed).removeClass(classFollowed);
			}
			if(toCenter)
				elem.css('margin-left', (elem.parent().width() - elem.width()) / 2 + 'px');
		}

		$('.btn-follow')
			.each(function(){
				setText($(this));
			})
			.click(function(){
				var $this = $(this);
				var userId = $this.data('user'),
					followed = $this.data('followed');

				var toFollow;
				if(followed == 1)
					toFollow = false;
				else
					toFollow = true;

				setFollow(userId, toFollow, function(err){
					if(err)
						alert(err);
					else{
						if(toFollow){
							$this.data('followed', 1)
						}else{
							$this.data('followed', 0);
						}
						setText($this);
					}
				});
			})
	}

	window.App = App;

})(window, jQuery);