package {
	import flash.events.MouseEvent;
	import flash.text.TextField;
	import net.wg.gui.components.controls.SoundButtonEx;
	import net.wg.gui.components.controls.ProgressBarAnim;
	import net.wg.gui.components.controls.ScrollBar
	import net.wg.infrastructure.base.AbstractWindowView;
	import net.wg.gui.components.advanced.vo.ProgressBarAnimVO;

	public class AutoupdaterLobbyWindow extends AbstractWindowView {
		
		public var autoupdExp:      TextField;
		public var autoupdCloseBtn: SoundButtonEx;
		
		public var  modsListStatus:    TextField;
		public var  modsListPrBarText: TextField;
		public var  modsListPrBar:     ProgressBarAnim;
		private var modsListPrBarVO:   ProgressBarAnimVO = new ProgressBarAnimVO(new Object());
		
		public var  filesStatus:         TextField;
		public var  filesText:           TextField;
		public var  filesTextScrollBar:  ScrollBar;
		public var  filesDataPrBarText:  TextField;
		public var  filesDataPrBar:      ProgressBarAnim;
		private var filesDataPrBarVO:    ProgressBarAnimVO = new ProgressBarAnimVO(new Object());
		public var  filesTotalPrBarText: TextField;
		public var  filesTotalPrBar:     ProgressBarAnim;
		private var filesTotalPrBarVO:   ProgressBarAnimVO = new ProgressBarAnimVO(new Object());
		
		public function AutoupdaterLobbyWindow() {
			super();
		}

		public function as_setupUpdateWindow(settings: Object): void {

			// apply window settings and invalidate main window size and size of inherited elements
			var _settings:Object      = settings;
			this.window.title         = _settings.window.title;
			this.window.width         = 560;
			this.window.height        = 437;
			this.window.useBottomBtns = _settings.window.useBottomBtns;
			this.window.invalidate();
			this.invalidate();
			
			
			// init progress bar values
			this.modsListPrBarVO.minValue = _settings.modsListPrBar.minValue;
			this.modsListPrBarVO.maxValue = _settings.modsListPrBar.maxValue;
			this.modsListPrBarVO.value    = _settings.modsListPrBar.value;
			this.modsListPrBarVO.useAnim  = _settings.modsListPrBar.useAnim;

			// set progress bar size and invalidate constraints
			this.modsListPrBar.setActualSize(_settings.modsListPrBar.width, _settings.modsListPrBar.height);
			if (modsListPrBarVO.value > 0) {
				this.modsListPrBar.setData(modsListPrBarVO);
			}
			
			
			this.filesTextScrollBar.scrollTarget = this.filesText;
			this.filesTextScrollBar.height       = this.filesText.height;
			this.filesTextScrollBar.x            = this.filesText.x + this.filesText.width;
			this.filesTextScrollBar.y            = this.filesText.y;
			
			// init progress bar values
			this.filesDataPrBarVO.minValue = _settings.filesDataPrBar.minValue;
			this.filesDataPrBarVO.maxValue = _settings.filesDataPrBar.maxValue;
			this.filesDataPrBarVO.value    = _settings.filesDataPrBar.value;
			this.filesDataPrBarVO.useAnim  = _settings.filesDataPrBar.useAnim;

			// set progress bar size and invalidate constraints
			this.filesDataPrBar.setActualSize(_settings.filesDataPrBar.width, _settings.filesDataPrBar.height);
			if (filesDataPrBarVO.value > 0) {
				this.filesDataPrBar.setData(filesDataPrBarVO);
			}
			
			// init progress bar values
			this.filesTotalPrBarVO.minValue = _settings.filesTotalPrBar.minValue;
			this.filesTotalPrBarVO.maxValue = _settings.filesTotalPrBar.maxValue;
			this.filesTotalPrBarVO.value    = _settings.filesTotalPrBar.value;
			this.filesTotalPrBarVO.useAnim  = _settings.filesTotalPrBar.useAnim;

			// set progress bar size and invalidate constraints
			this.filesTotalPrBar.setActualSize(_settings.filesTotalPrBar.width, _settings.filesTotalPrBar.height);
			if (filesTotalPrBarVO.value > 0) {
				this.filesTotalPrBar.setData(filesTotalPrBarVO);
			}
			
			
			// setup close button
			this.autoupdCloseBtn.setActualSize(_settings.autoupdCloseBtn.width, _settings.autoupdCloseBtn.height);
			this.autoupdCloseBtn.addEventListener(MouseEvent.CLICK, this.cancelClick);
			this.autoupdCloseBtn.label = _settings.autoupdCloseBtn.label;
		}
		
		public function as_setExpTime(text: String): void {
			this.autoupdExp.htmlText = text;
		}
		
		public function as_setTitle(text: String): void {
			this.window.title = text;
		}
		
		
		public function as_setModsListStatus(text: String): void {
			this.modsListStatus.htmlText = text;
		}
		
		public function as_setModsListRawProgress(value: int): void {
			this.modsListPrBarVO.value = value;
			this.modsListPrBar.setData(modsListPrBarVO);
		}
		
		public function as_setModsListProgress(text:String, value: int): void {
			this.modsListPrBarText.htmlText = text;
			this.as_setModsListRawProgress(value);
		}
		
		
		public function as_setFilesStatus(text: String): void {
			this.filesStatus.htmlText = text;
		}
		
		public function as_writeFilesText(text: String): void {
			this.filesText.htmlText += text;
		}
		
		public function as_writeLineFilesText(text: String): void {
			this.as_writeFilesText(text + "<br>");
		}
		
		public function as_setFilesDataRawProgress(value: int): void {
			this.filesDataPrBarVO.value = value;
			this.filesDataPrBar.setData(filesDataPrBarVO);
		}
		
		public function as_setFilesDataProgress(text:String, value: int): void {
			this.filesDataPrBarText.htmlText = text;
			this.as_setFilesDataRawProgress(value);
		}
		
		public function as_setFilesTotalRawProgress(value: int): void {
			this.filesTotalPrBarVO.value = value;
			this.filesTotalPrBar.setData(filesTotalPrBarVO);
		}
		
		public function as_setFilesTotalProgress(text:String, value: int): void {
			this.filesTotalPrBarText.htmlText = text;
			this.as_setFilesTotalRawProgress(value);
		}
		

		private function cancelClick(e: MouseEvent): void {
			this.handleWindowClose();
		}

		override protected function onPopulate(): void {
			super.onPopulate();
		}

		override protected function onDispose(): void {
			this.autoupdCloseBtn.removeEventListener(MouseEvent.CLICK, this.cancelClick);
			super.onDispose();
		}
	}
}