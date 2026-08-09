var player;
var meritKingConfig = {
	"source": {
		"group": {
			"id": "	f9a95e0d-e004-4aaf-bd62-8db807b3a5d7",
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
    player = new NanoPlayer("meritKingPlayer");
    player.setup(meritKingConfig).then(function (meritKingConfig) {
        console.log("setup success");
        console.log("meritKingConfig: " + JSON.stringify(meritKingConfig, undefined, 4));
    }, function (error) {
        alert(error.message);
    });
});