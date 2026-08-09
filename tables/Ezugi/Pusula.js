var player;
var pulsaConfig = {
	"source": {
		"group": {
			"id": "6e70dd5a-d77b-4b4b-a6d1-abadf37c214c",
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
    player = new NanoPlayer("pulsaPlayer");
    player.setup(pulsaConfig).then(function (pulsaConfig) {
        console.log("setup success");
        console.log("pulsaConfig: " + JSON.stringify(pulsaConfig, undefined, 4));
    }, function (error) {
        alert(error.message);
    });
});