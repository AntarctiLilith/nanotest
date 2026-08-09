var player;
var twelveDThunderConfig = {
	"source": {
		"group": {
			"id": "473203c6-6435-4277-8900-0f50243789b4",
			"apiurl": "https://bintu.nanostream.cloud"
		},
		"options": {
			"adaption": {
				"rule": "deviationOfMean2"
			}
		},
		"startIndex": 0
	},
	"playback": {
		"enableMediaOverQuic": true,
		"latencyControlMode": "balancedadaptive",
		"autoplay": true,
		"automute": true,
		"faststart": true
	},
	"style": {
		"width": "auto",
		"height": "auto"
	}
};
document.addEventListener('DOMContentLoaded', function () {
    player = new NanoPlayer("12DThunderPlayer");
    player.setup(twelveDThunderConfig).then(function (twelveDThunderConfig) {
        console.log("setup success");
        console.log("twelveDThunderConfig: " + JSON.stringify(twelveDThunderConfig, undefined, 4));
    }, function (error) {
        alert(error.message);
    });
});