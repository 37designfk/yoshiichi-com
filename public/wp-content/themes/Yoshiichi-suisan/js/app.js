// 即時実行関数で初期状態を設定
(function() {
    const isInternal = performance.navigation.type === 0 && 
                      document.referrer && 
                      new URL(document.referrer).origin === window.location.origin;
    
    if (isInternal) {
        document.documentElement.classList.add('internal-navigation');
    }
})();

const fvcontainer = document.querySelector('.fv-container');
const heroVideo = document.getElementById('hero-video');
let mainTimeline; // タイムラインをグローバルに保持

// スクロールとタッチイベントを無効にする関数
function disableScroll() {
    document.body.style.overflow = 'hidden';
    document.body.addEventListener('touchmove', preventDefault, { passive: false });
}

// スクロールとタッチイベントを有効にする関数
function enableScroll() {
    document.body.style.overflow = '';
    document.body.removeEventListener('touchmove', preventDefault, { passive: false });
}

// デフォルトのイベントを防ぐための関数
function preventDefault(e) {
    e.preventDefault();
}

// 内部リンクかどうかを判定する関数
function isInternalNavigation() {
    return performance.navigation.type === 0 && 
           document.referrer && 
           new URL(document.referrer).origin === window.location.origin;
}

// URLのハッシュを確認する関数
function checkUrlHash() {
    const hash = window.location.hash;
    return hash === '#tp';
}

// アニメーションをスキップする関数
function skipAnimation() {
    fvcontainer.style.display = 'none';
    enableScroll();
    if (heroVideo) {
        heroVideo.currentTime = 0;
        heroVideo.play();
    }
}

// 初期化時の処理
function initialize() {
    // 内部リンクからの遷移の場合
    if (isInternalNavigation()) {
        skipAnimation();
        return;
    }
    
    // #tp からの遷移の場合
    if (checkUrlHash()) {
        enableScroll();
        return;
    }
    
    // それ以外の場合は通常の処理
    disableScroll();
    document.documentElement.classList.remove('internal-navigation');
    startAnimation();
}

// アニメーションを開始する関数
function startAnimation() {
    mainTimeline = gsap.timeline();

    mainTimeline.to(".fv-curtain", { 
        yPercent: -100,
        duration: 0.5,
        delay: 5,
        ease: "power3.out",
    });

    mainTimeline.to(".fv-wrap", { 
        opacity: 0,
    });

    mainTimeline.to(".fv-container", { 
        yPercent: 100,
        duration: 1,
        onComplete: () => {
            fvcontainer.style.display = 'none';
            enableScroll();

            if (heroVideo) {
                heroVideo.currentTime = 0;
                heroVideo.play();
            }
        }
    });

    mainTimeline.from(".fade-left", {
        opacity: 0,
        x: -50,
        duration: 1,
        delay: -0.5,
        ease: "power2.out"
    });

    // クリックイベントの設定
    setupSkipEvent();
}


/*
// クリックスキップイベントの設定
function setupSkipEvent() {
    const myDiv = document.getElementById("fv-container");
    if (myDiv) {
        myDiv.addEventListener("click", function() {
            if (mainTimeline) {
                mainTimeline.seek(4.5);
            }

            if (heroVideo) {
                heroVideo.currentTime = 0;
                heroVideo.play();
            }
        });
    }
}
*/

// クリックスキップイベントの設定
function setupSkipEvent() {
    const myDiv = document.getElementById("fv-container");
    if (myDiv) {
        myDiv.addEventListener("click", function handleSkip() {
            if (mainTimeline && mainTimeline.isActive()) {
                // タイムラインを停止して最終状態に進める
                mainTimeline.progress(1).kill();
            }

            if (heroVideo) {
                heroVideo.currentTime = 0;
                heroVideo.play();
            }

            // コンテナを非表示にしてスクロールを有効化
            fvcontainer.style.display = 'none';
            enableScroll();

            // イベントリスナーを削除して、再実行を防止
            myDiv.removeEventListener("click", handleSkip);
        });
    }
}

// DOMContentLoaded時の処理
window.addEventListener("DOMContentLoaded", function(){
    initialize();
    
    // リロード時にトップへスクロール
    window.addEventListener("beforeunload", function(){
        window.scrollTo(0, 0);
    });
});