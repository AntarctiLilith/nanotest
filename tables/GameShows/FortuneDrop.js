var player;
var fortuneDropConfig = {
	"source": {
		"group": {
			"id": "59dbd70b-b019-4ec5-bc7b-5299834f87f8",
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
    player = new NanoPlayer("fortuneDropPlayer");
    player.setup(fortuneDropConfig).then(function (fortuneDropConfig) {
        console.log("setup success");
        console.log("fortuneDropConfig: " + JSON.stringify(fortuneDropConfig, undefined, 4));
    }, function (error) {
        alert(error.message);
    });
});