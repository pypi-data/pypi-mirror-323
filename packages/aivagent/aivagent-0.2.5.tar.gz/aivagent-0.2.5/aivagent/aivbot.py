'''
    ### AIV平台Bot管理模块  ###
        以插件的模式组织管理AI应用程序,以单进程、多进程、服务器守护进程等多种运行模式外挂Bot程序,实现
        多功能的AI应用平台。并可通过AIV服务器程序输出到多种终端。
    
    * 终端(以workflow模式)支持以下平台:
        - 小程序：微信小程序、抖音小程序、支付宝小程序、百度小程序等几乎所有小程序平台及微信公众号程序
        - 原生程序: android、ios、Harmony 
        - H5程序: pc、mac、公众号
        - Electron 框架应用程序

    * 运行 run() 函数前,需要正确使用 pip install aivagent 模块, 并且把它的路径添加到 sys.path 搜索路径中
            也可以使用 initPath() 初始化路径
    * 此模块的 run()函数,在用户的Bot模块中被调用,必须是最先运行的代码, run()必须写__main__里;
    * aivBot 变量只能在Api函数内使用  from aivagent.aivbot import aivBot 导入使用   

    * Bot 以Service模式初始化时运行顺序:
        init()
        setup()

    * 客户端获取Bot Api函数参数时运行顺序:
        init()
        setup()
        _onStartTask()
        param()

    * 客户端调用Bot Api函数时运行顺序:
        init()
        setup()
        _onStartTask()
        execute() # 默认的执行函数(如果客户端指定Bot Api函数,则运行对应的函数)

    * 客户端禁止调用Bot中以 '_'开头定义的函数

    * 关于调试: 找到安装目录下: aivc/bin/debug.bat,直接运行即可(运行前要把AIV AGI服务程序关闭);
    * AIV AGI 服务程序管理地址: http://127.0.0.1:28067/
    * 常用的工具函数,统一放在 aivtool.py 模块中(比如生成文件md5码的函数)
        (2023.12)
'''
import sys,os,time,traceback, asyncio
from loguru import logger

# 注意: aivBot变量在Bot的Api函数外使用 from aivagent.aivbot import aivBot 引入, 可能为None值. 2024.11
# 因此, 只能在函数内再导入一次使用!!!
aivBot = None   
    
def initPath(path, addParent= True):
    '''
        2024.11
        把当前目录、__file__所在目录、上级目录都添加到sys.path的搜索路径中
        # path 为py代码文件变量: __file__
    '''
    rootPath = os.path.dirname(os.path.abspath(path))
    sys.path.append('.')        # 添加根目录(不一定是当前的文件目录)
    sys.path.append(rootPath)   # 添加当前的文件目录
    if addParent:
        sys.path.append(os.path.dirname(rootPath))

## 1、初始化Aiv Bot 的第一个函数=======================================================================
def run(botId=None, logLevel = 'INFO', option = None) -> None:
    '''
        注册AIV平台的Bot
        @param botId:   Aiv平台分配的bot唯一的token
        @param logLevel: 可选 'DEBUG','INFO','SUCCESS','WARNING','ERROR','CRITICAL' 
        @param option: 当前Bot的参数(如: reload,timeout, ...)

        - desc
        * 此函数,必须是在用户Bot中执行的第一行代码(__main__中,但应该在bot api函数<以api开头>声明之后)
        * 当前模块下,所有非'_'开头的函数,都自动注册为AIV系统的iBot接口函数
        * run()函数必须在模块的 "__main__" 后面调用,并且不能包裹在函数里面调用!
        * 每一个Bot模块都运行在一个独立进程中, 可以在option参数设置 reLoad: True 开启代码修改自动更新客户端iBot接口功能
        * 注意: 在Aivc.exe启动时, 在启动并初始化所有Bot进程, 如果用户对某个Bot开启了 option['reload'] = True, 则初始化后,
                Bot子进程不会退出。因此,Bot的开发目录将被独占(window下不能改名,不能被删除)
    '''
    try:
        import inspect
        # inspect.stack() 返回函数的调用栈
        frame = inspect.stack()
        if frame[1][3] != '<module>':
            raise Exception('run() 函数必须在用户的bot模块"__main__"下调用,且不能包裹在函数中调用')
        
        obj = inspect.getmembers(frame[1][0]) #  
        #数据是[(,) , (,) , (,) , (,)] 这样的
        globalvar = None 
        for tup in obj:
            if tup[0]=='f_globals': #字段'f_globals'记录的值 ,等同于函数 globals() 返回的值, 但globals()必须在自己的模块下运行,灵活性不足
                globalvar = tup[1]
                break

        from .aivapp import _aivAppInit #初始化全局路径、环境变量、logger
        _aivAppInit(globalvar['__file__'],False, loglevel=logLevel)
        
        
        aivBotInfo = AivBotInfo()
        # global botName
        # botName = aivBotInfo.botName

        # 检测某些模块是否安装(目的是提醒开发者,减少无谓的时间浪费) 2024.6
        def _checkModuleInstalled(moduleName, isMust= True):
            import importlib
            try:
                importlib.import_module(moduleName)
            except ImportError:
                msg = f"Bot: {aivBotInfo.botName} 检测发现 {moduleName} 未安装! 请在cmd窗口运行: pip install 安装"
                if moduleName == 'loguru':
                    print(msg)
                else:
                    if isMust: #必须安装的包, 给出警告
                        logger.warning(msg)
                    else:
                        logger.debug(msg+" (可选)")

        # logger.warning('Bot的Option是: {}'.format(aivBot.botOption))
                    
        _checkModuleInstalled('loguru')
        _checkModuleInstalled('psutil')
        _checkModuleInstalled('cv2', False)  #对于用到opencv-python包,在用nuitka编译,如果在main.exe代码中不显式import cv2
                                             # 会导至以下错误： ImportError: DLL load failed while importing cv2: 找不到指定的模块。
                                             # cv2 用 pip install opencv-python 安装
        
        import asyncio
        # 设置日志保存的文件路径,每一个iBot进程都要设置一次(loguru) 2024.2
        botPath = os.path.dirname(os.path.abspath(globalvar['__file__'])) #Bot程序路径
        
        from .aivtool import setLogFile  
        #设置日志保存的文件路径和级别,默认把WARNING级别的日志保存在执行程序目录的botError.log文件中(但不影响控制台输出的日志) 2024.2 
        logFile = os.path.join(botPath,'botError.log') #在bot模块根目录下生成一个日志文件 2024.3
        
        setLogFile(logFile, logLevel= 'INFO')  #默认只显示 INFO信息(只影响写入本地文件的日志等级,不影响控制台输入日志的等级)
        
        global aivBot   # 2024.11
        aivBot = AivBot()
        aivBot.botInfo = aivBotInfo  # AivBotInfo 类
        aivBot.botInfo.path = botPath
        aivBot.botInfo.botId = botId
        aivBot.botOption = option # 当前Bot的配置内容
        aivBot.botInfo.logLevel = logLevel
        
        initFun,setupFun = aivBot._regBotApi(globalvar)
        if initFun is not None:
            initFun()   # 调用 init()函数 < 如果有的话 >

        from .aivmmap import AivBotMmap
        aivBotMmap = AivBotMmap(aivBot)
        aivBot.aivBotMmap = aivBotMmap

        # aivBot.aivBotMmap.onStartTask = aivBot._onStartTask #响应AGI调用Bot的api接口执行任务的事件

        ''' 2023.11
            用线程检测进程 wcPid 是否退出
            用线程检测 wcPid 进程是否退出(不是用 asyncio 协程,是用 threading 检测),如果wcPid进程退出,线程也跟着退出 
            原因是 asyncio的所有子协程都是在进程的主线程运行, 当AIV平台的bot模块运行任务时,基本是上独占模式(死循环)
            这样如果用户中止任务,虽然bot模块也收到 TaskState.taskProExit 信号,但 aivBotMmap.run() 阻塞在运行任务上
            没办法响应  TaskState.taskProExit 信号, 但线程是可以的.因此,在 aivBotMmap.run()检测任务是否中止信号上,
            另外用线程 threading 建立一个独立于主线程的子线程,用于检测wcPid是否退出(这里是检测aivwc.py的进程)。这样,
            当协程阻塞时,threading的线程仍然可用,可以保证主进程下达的中止指令可以被执行。
        '''
        aivBot.aivBotMmap.createCheckPidThread([aivBot.botInfo.ppid,aivBot.botInfo.wcpid],aivBot.botInfo.botName)

        if option.get('reload', False):
            logger.warning(f'Bot模块: {aivBot.botInfo.botName} 启动成功. 已经打开 "reload"模式,建议正式发布后关闭.')
        else:
            logger.debug(f'Bot模块: {aivBot.botInfo.botName} 启动成功.')

        # 清除除第一个元素以外的参数
        sys.argv[1:] = []  # 清除主进程启动 Bot 程序时带的参数, 避免Bot启动自身业务进程时受这些参数的影响 2024.7

        # 协程函数
        async def _main():
            # aivBotMmap的功能主要是检测是否有新任务(抢单),二是检测任务的状态,如果任务被前端取消,则马上退出进程
            # 另外,也要不断检测任务是否超时,超时就自动中止进程 2023.11
            asyncio.create_task(aivBot.aivBotMmap.run())  
            while True:
                await asyncio.sleep(0.2) #只要主程序不退出,上面的协程就一直运行

        if setupFun is not None:
            setupFun()  # 最后调用 setup()函数 <如果有的话>
        asyncio.run(_main())

    except Exception as e:
        logger.warning(f'Bot模块: {aivBot.botInfo.botName} > run() 出错! Error= {e}')
        traceback.print_exc()  # 输出完整的堆栈跟踪信息



class AivBotInfo:
    '''
        当前运行的Bot对象的信息汇总
    '''
    def __init__(self) -> None:
        self.logLevel = 'INFO'
        self.pid = os.getpid() # 当前进程的PID
        self.botId = ''
        self.path = '' #主执行文件路径(含文件名)

        if len(sys.argv)>1:
            self.ppid = int(sys.argv[1]) #父进程的pid,根据父进程pid,如果它退出,自己也退出
        if len(sys.argv)>2:
            self.taskMMAPName = sys.argv[2] #这个是前端传过来的 taskId (32位长度的字符串,全球唯一), 当前任务启用的共享内存名称
        if len(sys.argv)>3:
            self.wcpid = int(sys.argv[3])  # 同级子进程 wc的进程pid,如果在命令行参数中传入此值,则可以根据此值,同步退出进程
        if len(sys.argv)>4:
            self.botName = sys.argv[4] #第4个参数传 botName 2023.12
        if len(sys.argv)>5:
            # 所有参数都必须转成str类型传进子进程,因为这里要对比 == 'True'
            self.isService = sys.argv[5].lower() == 'true' #第5个参数传决定当前进程是任务进程是否自动启动(作用服务程序模块) 2024.11
            

    def getBotInfo(self):
        '''
            返回当前模块的信息
        '''
        return {
            'logLevel': self.logLevel,
            'botName': self.botName,
            'botId' : self.botId,
            'path': self.path,
            'pid': self.pid,
            'ppid': self.ppid,
            'wcpid': self.wcpid,
            'taskMMAPName': self.taskMMAPName,
            'isService': self.isService
        }

class AivBot:
    def __init__(self) -> None:
        self.botInfo = None # AivBotInfo 类
        self.task = None #用于临时记录任务信息, 在 addFileToTaskOutParam()调用
        self.botOption = None
        self.api = [] # 记录当前bot模块所有的Api信息
        # self.cmd = ''   #调用iBot的Api时指令类型 ('init','run' 可选)
        self.isSetResult= False # 用户是否设置了返回值


    def _regBotApi(self,glob:dict): #利用 globals() 读取指定模块的所有函数名
        ''' 2023.10
        ### 注册 bot 模块
        * 参数 glob 包含有模块的函数及函数地址！
        * 将自动注册所有用户自定义的函数!(除以横线'_'开头的和run()函数)
        * Api 函数必须有两个参数,分别是(cmd, parser)
        * 可以导入其它模块的函数成为api函数 : from xxx.xxx import xxxxfun
        * 请勿直接调用AivBot以'_'开头的函数
        '''
        from .aivtool import checkReservedName
        lst = list(glob)
        import types
        # logger.debug('bot 模块所有参数如下 (包含模块内所有函数、方法名称和内存地址): \n{}'.format(glob))

        hasInitFun = None
        hasSetupFun = None
        from loguru import logger
        #循环模块的所有函数,把aiv 开头的函数自动导入----------------------------------
        for fun_name in lst:
            fun = glob[fun_name]   
            # logger.warning(f'{self.botInfo.botName} 的函数名: {fun_name}')

            if (type(fun) == types.FunctionType) or (type(fun) == types.MethodType): #判断是方法（而不是属性)
                if fun_name != 'run' and not fun_name.startswith('_'): #排除检测 run()函数和 "_"开头的函数 2024.3 ,其它函数都可以导出                              
                    if not checkReservedName(fun_name,'Bot: {} 的Api函数'.format(self.botInfo.botName)):
                        
                        title = ''
                        if fun.__doc__ is not None:
                            title = fun.__doc__.strip()[:16] #读取函数备注内容,取前16个字符

                        # apidict 只记录静态的信息
                        apidict = {'bot':self.botInfo.botName, 'name':fun_name, 'title': title, 'fun':fun,'paramIn':None,'apiOption':None}
                        self.api.append(apidict)

                        # callParam = {'bot':self, 'sysInfo':aivBotMmap.sysInfo} #把任务信息和系统信息打包,一起给bot的api传参  
                        # fun('init', callParam) #初始化Api函数

                        if fun_name.lower() == 'init':
                            # logger.warning(f' {self.botInfo.botName} 找到函数 init')
                            hasInitFun = fun
                        if fun_name.lower() == 'setup':
                            # logger.warning(f' {self.botInfo.botName} 找到函数 setup')

                            hasSetupFun = fun
                    else:
                        logger.warning(f'请勿使用系统保留字命名函数名: {fun_name}')
                      

        logger.debug(f'Bot: {self.botInfo.botName} - iBot 接口列表初始化完成.')

        if len(self.api)==0:
            logger.warning(f'Bot: {self.botInfo.botName} 还没有注册任何 iBot 接口.')
        else:
            logger.debug(f'Bot: {self.botInfo.botName} > run() 成功启动! \n---- iBot 接口列表是 ----: \n{self.api}')

        return hasInitFun, hasSetupFun   # 如果有初始化函数和安装函数就返回(给主过程调用)


    async def _getApiParam(self, apiName, apiFun):
        ''' 2024.11
            获取Api函数的参数
            参数的配置数据格式如下:  ('type' 可选类型有: 'file'、'text'、'bool'、'combo'、'number'、'seed')  # seed 是随机数 2025.1
                {'name': 'soundMode', 'title': '声音模型', 'option': {'type': 'combo', 'vaules': ['v1', 'v2', 'v3']}, 'default': 'v2', 'hasDefault': True}        
            或  {'name': 'level', 'title':'等级','order': 10,  'option': {'type': 'number', 'min': 1, 'max': 10, 'step': 0.1 , 'default': 2, 'hasDefault': True}        

            注意: 'option'字段必须由 init()函数处理并添加,默认没有此字段。像 'prompt'系统默认为 'text'类型字段,
            'order' 属性默认值10, 使参数在用户设置界面排序,越大的排在前面
            带有file的名称参数默认为 'file'类型字段,像 'videoFile'、'wavFile' 自动识别为 type='file'类型
            参照以上内容,开发者可以使用 init() 函数处理成以上格式。'title'还可以写成  'title': {'zh': '声音模型', 'en': 'sound model'}


            以上设置只是在AIV客户端设计工作流(workflow)时使用,在Ai应用发布后,这里的设置不会影响到设计好的工作流。
        '''
        # 获取函数的参数信息并返回 2024.11
        # logger.debug('开始运行 getApiParam...')
        import inspect
        signature = inspect.signature(apiFun)
        apiParamList = []
        resData= {}
        for param in signature.parameters.values():
            paramData = {
                'name': param.name,
                # 'kind': param.kind,
                'hasDefault': param.default is not inspect.Parameter.empty,
                'default': param.default if param.default is not inspect.Parameter.empty else 'None'
            }
            apiParamList.append(paramData)
        resData['params'] = apiParamList        # 获取参数列表
        # 获取函数的说明(可以在说明里进一步说明参数的类型, 如:file,string,boolean,combo 等)
        resData['doc'] = inspect.getdoc(apiFun) 
        resData['coName'] = self.botInfo.botName
        resData['coApi'] = apiName
        import asyncio

        logger.debug(f'当前的 aivBot== {aivBot}' )
        for apiObj in self.api:
            if apiObj['name'].strip().lower() == 'param': 
            # 如果当前Bot模块有 init 函数,则把初始生成的数据交给 init() 处理一遍
            # (在init函数中可以对参数进行更详细的说明, 附带详细的json格式文档 2024.11
                try:
                    paramFun = apiObj['fun']
                    if asyncio.iscoroutinefunction(paramFun):   #检测如果是异步函数(函数用 async def xxx() 定义的),则用 await 调用 2024.6
                        newData= await paramFun(resData)        #调用用户Bot的api函数 2024.4
                    else:
                        newData= paramFun(resData)

                    if newData is not None: # 如果用户在 param()函数中没有修改 resData的值
                        resData = newData
                except Exception as e:
                    logger.warning(f'param 函数错误! Error-> {e}')
                break
    
        logger.debug(f'获取的参数结果是: {resData}')
        return resData
    
    def setParam(self,param,  default, title:str, order:int):
        if default is not None:
            param['default'] = default
            param['hasDefault'] = True
        if title is not None:
            param['title'] = title
        param['order'] = order

    # 设置 number 类型参数
    def setNumberParam(self,params, paramName: str, max, min, step: float=1, default=None, title:str =None, order:int = 10):
        if not isinstance(params, list) and params.get('params', None) is not None:
            params = params['params']
        for param in params:
            if param['name'].lower() == paramName.lower():
                # number 类型参数数据格式如下:
                param['option'] = {
                    'type': 'number',
                    'max': max,
                    'min': min,
                    'step': step,
                }
                self.setParam(param, default, title, order)
                break
    
    # 设置combo(下拉框) 类型参数
    def setComboParam(self, params, paramName: str, values: list, default=None, title:str =None, order:int = 10):
        if not isinstance(params, list) and params.get('params', None) is not None:
            params = params['params']
        for param in params:
            if param['name'].lower() == paramName.lower():
                if len(values)==0 :
                    logger.warning(f'没有设置 {paramName} 参数的 values 值.')
                # combo 类型参数数据格式如下:
                param['option'] = {
                    'type': 'combo',
                    'values': values
                }
                self.setParam(param, default, title, order)
                break

    # 设置文本类型参数
    def setTextParam(self, params, paramName: str, multi:bool = True, default=None, title:str =None, order:int = 10):
        if not isinstance(params, list) and params.get('params', None) is not None:
            params = params['params']
        for param in params:
            if param['name'].lower() == paramName.lower():
                # text 类型参数数据格式如下:
                param['option'] = {
                    'type': 'text',
                    'multi': multi
                }
                self.setParam(param, default, title, order)
                break

    # 设置 bool 类型参数:
    def setBoolParam(self, params, paramName: str, default=None, title:str =None, order:int = 10):
        if not isinstance(params, list) and params.get('params', None) is not None:
            params = params['params']
        for param in params:
            if param['name'].lower() == paramName.lower():
                # bool 类型参数数据格式如下:
                param['option'] = {
                    'type': 'bool'
                }
                self.setParam(param, default, title, order)
                break

    # 设置文件类型参数
    def setFileParam(self, params, paramName: str, default=None, title:str =None, order:int = 10):
        if not isinstance(params, list) and params.get('params', None) is not None:
            params = params['params']
        for param in params:
            if param['name'].lower() == paramName.lower():
                # 文件类型参数数据格式如下:
                param['option'] = {
                    'type': 'file'
                }
                self.setParam(param, default, title, order)
                break


    async def _onStartTask(self,task):
        ''' 2023.09
            @param task: 任务信息
            * 请勿直接调用AivBot以'_'开头的函数
        '''
        import asyncio
        logger.debug('aivBot 收到的启动任务参数是: task ==> {}'.format(task))

        # ======= 调api的参数准备 ============================================== 1
        apiName = None
        self.isSetResult = False
        try:
            # 检测是否有输入参数 'paramIn'
            if task['param'] is None:
                task['param']= {}
            
            self.task = task
            self.task['apiTimeStart'] = int(time.time()*1000) # api的启动时间(毫秒)
            self.task['outputs'] = None

            # 检查是否有调用的bot api 函数名
            apiName = task.get('coApi',None)
            if apiName is None:
                logger.error(f'客户端没有指定要调用的bot iBot接口名称: {apiName} ')

            if len(self.api)==0:
                logger.error('检测到Bot: {} 无注册任何iBot函数.'.format(self.botInfo.botName))

            apiName = apiName.strip()
            # 根据任务给定的api函数名,找出 bot 对应的真实函数 (通过 botName)
            apiFun = None
            # apiOption = None
            for apiObj in self.api:
                if apiObj['name'].strip().lower() == apiName.lower():

                    apiFun = apiObj['fun']
                    # apiOption = apiObj['apiOption'] #对于 api的配置,用户可以在api函数中自行利用
                    break

            if apiFun is None:
                raise Exception(f'本地Bot模块无api函数:[ {apiName} ]! 请检测Bot模块的api函数名称.')
            
            # ============正式调用bot api 函数 =========================================================== 2 
            from .aivmmap import TaskResultCode

            param:dict = task['param']
            # logger.warning(f'收到的参数是 ： {param}')
            if param.get('$getApiParam', None) is not None: 
                resData = await self._getApiParam(apiName, apiFun)
            
            else: # 执行客户端指定的Bot函数
                if asyncio.iscoroutinefunction(apiFun):  #检测如果是异步函数(函数用 async def xxx() 定义的),则用 await 调用 2024.6
                    resData= await apiFun(**param) #调用用户Bot的api函数 2024.4
                else:
                    resData= apiFun(**param)

                # logger.warning('Bot api {} 运行返回结果是: {}'.format(apiName,retTask))
            # -----------------------------------------------------------------------
                
                # apiFun()返回结果只能是一个对象: {'files': [xxx], 'text': [xxx]}, 而且'files'或'text'必须至少有一个
                # 如果apiFun()函数只返回一个字符串,则会组装成 {'files': [xxx]}  这样的对象返回,默认是文件名数组
                if  isinstance(resData, str):   # 如果是返回一个str字符串,则默认做为文件名数组返回
                    resData = {'files': [resData]}

                # 提供一个返回数据的检测, 返回的结果必须是一个dict, 并且其中 'files' | 'text' 的一个属性 2024.10
                warnMsg = f'{self.botInfo.botName} 运行后返回的数据格式必须是:'+ ' {"files": xxx, "text": [xxx]}'
                if not isinstance(resData, dict):
                    logger.warning(warnMsg)
                else:   
                    if resData.get('files', None) is None and resData.get('text', None) is None:
                        logger.warning(warnMsg)
            
            self.task['outputs'] = resData   
            if self.isSetResult == False and  self.task['code'] != 200: #如果开发者没有设置返回结果, 则默认返回 code=200 的成功标志 2024.1
                # 设置成功标志
                self.aivBotMmap.setTaskResultCode(TaskResultCode.taskOk, f'Bot: {self.botInfo.botName} > {apiName} > 运行成功.') # 设置为OK状态

        except BaseException as e:
            import traceback
            traceback.print_exc()  # 输出完整的堆栈跟踪信息
            if self.botInfo.logLevel == 'DEBUG':            
                e = traceback.format_exc() # 获取出错的堆栈文本
            
            errMsg = f'Bot: {self.botInfo.botName}.{apiName}()  运行出错--->\n {e}'
            self.aivBotMmap.setTaskResultCode(TaskResultCode.taskSvr,errMsg) # 设置为服务器出错状态,并把出错信息回传js端 2023.12
        
        finally:
            self.task['apiTimeEnd'] = int(time.time()*1000) # api运行的结束时间(毫秒)
            self.aivBotMmap.endTask() # api函数内修改了task对象,也会同步返回
      

    def setResult(self, code, msg, isShow= True):
        ''' 2024.6
            设置当前Bot任务的返回信息
            @param code : 200 代表成功, 其它值均为失败
            @param msg  : 返回的消息

            默认在整个 iBot执行过程中无需调用 setResult 设置返回值, AIV会自动根据执行情况返回对应的内容。
            如果开发者需要根据自定义的情况返回错误/成功的信息,可以使用此函数
            * 如果设置了 code非200的值, 则表示Bot任务失败并返回客户端.
            * 也可以直接修改 aivBot.task里面的'result'对象
        '''

        self.aivBotMmap.setTaskResultCode(code, msg)
        if code != 200 and isShow:
            logger.warning(msg)
        self.isSetResult = True 
        return {"text": [msg]}


    def getOutPath(self,extName= '', childPath= None, defaultDir= 'out'):
        ''' 2024.3
            获取系统的输出文件目录 或 文件名

            @param extName 需要返回的文件名扩展名(如果设置了此参数,则函数会返回一个可用的文件名<扩展名是extName> )
            @param childPath : 需要创建的子目录 (如果指定此值,则在 aivc/data/out 目录下再创建一个子目录,如 comfyUI可以创建此目录)
                                Aiv系统将会定时清理aivc/data/out及其子目录
            @param defaultDir : 默认的输出目录, 可选值 'out', 'temp'
            @return : 返回一个在系统输出目录下的子目录或一个文件名 (一般在 d:/aivc/data/out)

            目的是在AIV系统默认的输出目录中创建一个子文件夹(一般是 d:/aivc/data/out 目录),用于保存iBot生成的数据
            可以在此系统目录基础上新建一个子目录给每个Bot专用 ,'sys.outDir'目录里的生成文件会定时被清理, 
            可以避免系统运行久了垃圾过多的问题. (每隔10分钟系统清理一次超过24小时未使用的临时文件,比如图片、视频等)
            客户端一般都是生成图片或程序即会自动下载, AGI端无需长期保存. 2024.3
        '''
        
        outPath = self.aivBotMmap.sysInfo['sys.outDir']  # 对应安装目录的 aivc/data/out
        if defaultDir.lower() == 'temp':
            outPath = self.aivBotMmap.sysInfo['sys.tempDir']  # 对应安装目录的 aivc/data/temp

        if childPath is not None:
            outPath = os.path.normpath(os.path.join(outPath,childPath)) #需要用normpath()规范化路径
            if not os.path.exists(outPath):
                os.mkdir(outPath)

        if extName is not None and extName != '':
            if not extName.startswith('.'):
                extName = '.' + extName
            import time
            fileName = str(int(time.time()))
            count = 0
            while True:
                filePath = os.path.normpath(os.path.join(outPath, fileName + extName))
                if not os.path.exists(filePath):
                    break # 如果 aivc/data/out 目录还没存在此文件,则把文件名返回
                else:
                    count += 1

            return filePath

        return outPath # 如果 extName 扩展名参数为'', 则返回目录名
    

    def getSysInfo(self):
        ''' 2024.1
            获取系统信息
            包含 AGI 行时间、系统使用的路径、软件版本等所有信息
        '''
        return self.aivBotMmap.sysInfo





    







