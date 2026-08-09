var player;
var carnivalTreasureConfig = {
	"source": {
		"group": {
			"id": "e7ebbfa1-57c8-41d6-a5bc-007ca0a43a22",
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
    player = new NanoPlayer("carnivalTreasurePlayer");
    player.setup(carnivalTreasureConfig).then(function (carnivalTreasureConfig) {
        console.log("setup success");
        console.log("carnivalTreasureConfig: " + JSON.stringify(carnivalTreasureConfig, undefined, 4));
    }, function (error) {
        alert(error.message);
    });
});