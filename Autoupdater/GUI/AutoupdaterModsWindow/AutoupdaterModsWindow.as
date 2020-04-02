package {
	import flash.events.MouseEvent;
	import flash.text.TextField;
	import net.wg.gui.components.controls.SoundButtonEx;
	import net.wg.gui.components.controls.ProgressBarAnim;
	import net.wg.gui.components.controls.ScrollBar
	import net.wg.infrastructure.base.AbstractWindowView;
	import net.wg.gui.components.advanced.vo.ProgressBarAnimVO;

	public class AutoupdaterModsWindow extends AbstractWindowView {
		
		public var autoupdTitle: TextField;
		
		public var autoupdCloseBtn:   SoundButtonEx;
		public var autoupdRestartBtn: SoundButtonEx;
		
		public var  filesText:           TextField;
		public var  filesTextScrollBar:  ScrollBar;
		
		public function AutoupdaterLobbyWindow() {
			super();
		}

		public function as_setupUpdateWindow(settings: Object): void {

			// apply window settings and invalidate main window size and size of inherited elements
			var _settings:Object      = settings;
			this.window.title         = _settings.window.title;
			this.window.width         = _settings.window.width;
			this.window.height        = _settings.window.height;
			this.window.useBottomBtns = true;
			this.window.invalidate();
			this.invalidate();
			
			
			this.filesTextScrollBar.scrollTarget = this.filesText;
			this.filesTextScrollBar.height       = this.filesText.height;
			this.filesTextScrollBar.x            = this.filesText.x + this.filesText.width;
			this.filesTextScrollBar.y            = this.filesText.y;
			
			
			// setup close button
			this.autoupdCloseBtn.setActualSize(_settings.autoupdCloseBtn.width, _settings.autoupdCloseBtn.height);
			this.autoupdCloseBtn.addEventListener(MouseEvent.CLICK, this.cancelClick);
			this.autoupdCloseBtn.label = _settings.autoupdCloseBtn.label;
			
			// setup close button
			this.autoupdRestartBtn.setActualSize(_settings.autoupdRestartBtn.width, _settings.autoupdRestartBtn.height);
			this.autoupdRestartBtn.addEventListener(MouseEvent.CLICK, this.restartClick);
			this.autoupdRestartBtn.label = _settings.autoupdRestartBtn.label;
		}
		
		public function as_setHtmlTitle(text: String): void {
			this.autoupdTitle.htmlText = text;
		}
		
		public function as_setTitle(text: String): void {
			this.window.title = text;
		}
		
		
		public function as_writeFilesText(text: String): void {
			this.filesText.htmlText += text;
		}
		
		public function as_writeLineFilesText(text: String): void {
			this.as_writeFilesText(text + "<br>");
		}
		
		private function restartClick(e: MouseEvent): void {
			this.handleWindowClose();
		}
		
		private function cancelClick(e: MouseEvent): void {
			this.handleWindowClose();
		}

		override protected function onPopulate(): void {
			super.onPopulate();
		}

		override protected function onDispose(): void {
			this.autoupdCloseBtn.removeEventListener(MouseEvent.CLICK, this.cancelClick);
			this.autoupdRestartBtn.removeEventListener(MouseEvent.CLICK, this.restartClick);
			super.onDispose();
		}
	}
}