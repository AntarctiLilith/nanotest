var player;
var madridConfig = {
	"source": {
		"group": {
			"id": "6e6c4737-e787-4cab-a937-1616dd36748f",
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
    player = new NanoPlayer("madridPlayer");
    player.setup(madridConfig).then(function (madridConfig) {
        console.log("setup success");
        console.log("madridConfig: " + JSON.stringify(madridConfig, undefined, 4));
    }, function (error) {
        alert(error.message);
    });
});