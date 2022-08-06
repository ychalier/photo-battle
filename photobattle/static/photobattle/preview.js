/**
 * Add the `preview` class to an element,
 * and provide an URL to a media element
 * has a `preview-img` or `preview-video` attribute.
 * When hovering on the .preview, a box with the media shows up.
 */


 const PREVIEW_SCREEN_SIZE_RATIO = 1;
 const PREVIEW_HOVER_DURATION = 1000; // ms
 var PREVIEW_CONTROLLER = null;
 
 
 class PreviewController {
 
     constructor() {
         this.el = null;
         this.visible = false;
         this.timeout = null;
         this.target = null;
         this.width = 0;
         this.height = 0;
         this.cursorX = null;
         this.cursorY = null;
     }
 
     createElement() {
         this.el = document.createElement("div");
         this.el.className = "preview-container";
         this.el.style.position = "fixed";
         this.el.style.pointerEvents = "none";
         document.body.appendChild(this.el);
     }
 
     handleMouseEnter(event, target) {
         let self = this;
         this.timeout = setTimeout(() => {
             self.show(target);
         }, PREVIEW_HOVER_DURATION);
     }
 
     handleMouseLeave(event, target) {
         if (this.timeout != null) {
             clearTimeout(this.timeout);
             this.timeout = null;
         }
         if (this.target == target) {
             this.hide();
         }
     }
 
     handleMouseMove(event) {
         this.cursorX = event.clientX;
         this.cursorY = event.clientY;
         this.updatePosition();
     }
 
     updatePosition() {
         let targetX = this.cursorX - this.width / 2;
         let targetY = this.cursorY - this.height / 2;
         this.el.style.left = Math.min(Math.max(0, targetX), window.innerWidth - this.width) + "px";
         this.el.style.top = Math.min(Math.max(0, targetY), window.innerHeight - this.height) + "px";
     }
 
     show(target) {
         this.timeout = null;
         let self = this;
         if (!target.hasAttribute("preview-img") && !target.hasAttribute("preview-video")) {
             // console.error("Preview element has no source:", this.el);
             return;
         }
         let media = null;
         let src = null;
         if (target.hasAttribute("preview-img")) {
             media = document.createElement("img");
             src = target.getAttribute("preview-img");
         } else {
             media = document.createElement("video");
             src = target.getAttribute("preview-video");
             media.muted = false;
             media.autoplay = true;
             media.loop = true;
         }
         let onLoad = () => {
             let mediaWidth = media.videoWidth ? media.videoWidth : media.naturalWidth;
             let mediaHeight = media.videoHeight ? media.videoHeight : media.naturalHeight;
             if (mediaWidth >= PREVIEW_SCREEN_SIZE_RATIO * window.innerWidth || mediaHeight >= PREVIEW_SCREEN_SIZE_RATIO * window.innerHeight) {
                 let windowAspect = window.innerWidth / window.innerHeight;
                 let mediaAspect = mediaWidth / mediaHeight;
                 if (mediaAspect > windowAspect) {
                     self.width = PREVIEW_SCREEN_SIZE_RATIO * window.innerWidth;
                     self.height = self.width / mediaAspect;
                 } else {
                     self.height = PREVIEW_SCREEN_SIZE_RATIO * window.innerHeight;
                     self.width = self.height * mediaAspect;
                 }
                 media.style.width = self.width + "px";
                 media.style.height = self.height + "px";
             } else {
                 self.height = mediaHeight;
                 self.width = mediaWidth;
             }
             self.updatePosition();
             if (self.target != null) self.target.style.cursor = "none";
         };
         media.addEventListener("load", onLoad);
         media.addEventListener("loadeddata", onLoad);
         this.el.appendChild(media);
         this.visible = true;
         this.target = target;
         media.src = src;
     }
 
     hide() {
         this.el.innerHTML = "";
         this.visible = false;
         this.target.style.cursor = null;
         this.target = null;
         this.width = 0;
         this.height = 0;
     }
 
     register(el) {
         el.addEventListener("mouseenter", (event) => this.handleMouseEnter(event, el));
         el.addEventListener("mouseleave", (event) => this.handleMouseLeave(event, el));
     }
 
 }
 
 
 window.addEventListener("load", () => {
     PREVIEW_CONTROLLER = new PreviewController();
     PREVIEW_CONTROLLER.createElement();
     document.body.addEventListener("mousemove", (event) => PREVIEW_CONTROLLER.handleMouseMove(event));
     document.querySelectorAll(".preview").forEach(el => PREVIEW_CONTROLLER.register(el));
 });