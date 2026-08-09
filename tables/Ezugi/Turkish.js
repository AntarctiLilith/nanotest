var player;
var turkishConfig = {
	"source": {
		"group": {
			"id": "b041b67c-030d-43e3-a082-b1e38866ce21",
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
    player = new NanoPlayer("turkishPlayer");
    player.setup(turkishConfig).then(function (turkishConfig) {
        console.log("setup success");
        console.log("turkishConfig: " + JSON.stringify(turkishConfig, undefined, 4));
    }, function (error) {
        alert(error.message);
    });
});