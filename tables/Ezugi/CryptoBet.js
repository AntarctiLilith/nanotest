var player;
var cryptoBetPlayer = {
	"source": {
		"group": {
			"id": "c80607b4-e254-461c-8648-6ff466995bed",
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
    player = new NanoPlayer("cryptoBetPlayer");
    player.setup(cryptoBetPlayer).then(function (cryptoBetPlayer) {
        console.log("setup success");
        console.log("cryptoBetPlayer: " + JSON.stringify(cryptoBetPlayer, undefined, 4));
    }, function (error) {
        alert(error.message);
    });
});