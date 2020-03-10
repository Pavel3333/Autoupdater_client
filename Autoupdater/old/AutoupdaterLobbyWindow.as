package
{
	import flash.events.MouseEvent;
	import flash.events.TextEvent;
	import flash.filters.DropShadowFilter;
	import flash.text.TextField;
	import net.wg.gui.components.controls.SoundButtonEx;
	import net.wg.infrastructure.base.AbstractWindowView;
	import net.wg.gui.components.controls.ProgressBar;
	import scaleform.clik.core.UIComponent;
	import flash.text.TextField;
	import flash.text.TextFormat;
	import flash.text.TextFieldAutoSize;
	import flash.events.MouseEvent;
	import flash.text.TextFormatAlign;
	
	public class InfoWindowSimpleUI extends AbstractWindowView
	{
		private var dataTF:TextField;
		
		private var versionTF:TextField;
		
		private var progress:ProgressBar;
		
		private var closeBtn:SoundButtonEx;
		
		public function InfoWindowSimpleUI()
		{
			super();
			var fmt:TextFormat = new TextFormat();
			var shadow:DropShadowFilter = new DropShadowFilter();
			shadow.angle = 90;
			shadow.strength = 1;
			shadow.quality = 15;
			shadow.distance = 1;
			
			fmt.size = 15;
			fmt.color = 0xECEADC;
			fmt.align = 'left';
			
			dataTF = new TextField();
			dataTF.width = 540;
			dataTF.height = 440;
			dataTF.x = 9;
			dataTF.y = 0;
			dataTF.multiline = true;
			dataTF.antiAliasType = "advanced";
			dataTF.wordWrap = false;
			dataTF.selectable = false;
			dataTF.defaultTextFormat = fmt;
			dataTF.filters = [shadow];
			this.addChild(this.dataTF);
			
			versionTF = new TextField();
			versionTF.width = 150;
			versionTF.height = 20;
			versionTF.x = 10;
			versionTF.y = 450;
			versionTF.multiline = false;
			versionTF.wordWrap = false;
			versionTF.selectable = false;
			this.addChild(versionTF);
			
			progress = new ProgressBar();
			progress.x = 10;
			progress.y = 480;
			this.addChild(progress);
			
			closeBtn = SoundButtonEx(App.utils.classFactory.getComponent("ButtonNormal", SoundButtonEx));
			closeBtn.setActualSize(100, 22);
			closeBtn.x = 460;
			closeBtn.y = 449;
			closeBtn.addEventListener(MouseEvent.CLICK, this.cancelClick);
			this.addChild(closeBtn);
		}

		public function as_setData(cfg:Object):void
		{
			this.window.title = cfg.title;
			closeBtn.label = cfg.btnText;
			versionTF.htmlText = cfg.version;
			dataTF.htmlText = cfg.textData;
		}

		private function cancelClick(e:MouseEvent):void
		{
			this.handleWindowClose();
		}

		override protected function onPopulate():void
		{
			super.onPopulate();
			this.width = 560;
			this.height = 470;
			this.window.useBottomBtns = true;
		}
		
		override protected function onDispose():void
		{
			closeBtn.removeEventListener(MouseEvent.CLICK, this.cancelClick);
			closeBtn = null;
			dataTF = null;
			versionTF = null;
			super.onDispose();
		}
	}
}