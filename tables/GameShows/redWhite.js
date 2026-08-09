var player;
var redWhiteConfig = {
	"source": {
		"group": {
			"id": "b3155ab9-73ce-4aca-963d-6dd506405150",
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
    player = new NanoPlayer("redWhitePlayer");
    player.setup(redWhiteConfig).then(function (redWhiteConfig) {
        console.log("setup success");
        console.log("redWhiteConfig: " + JSON.stringify(redWhiteConfig, undefined, 4));
    }, function (error) {
        alert(error.message);
    });
});