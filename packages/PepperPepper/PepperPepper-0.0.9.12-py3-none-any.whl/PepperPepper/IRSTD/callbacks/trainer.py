from PepperPepper.environment import torch, ml_collections, DataLoader, tqdm, SummaryWriter, os, time, random, np
from PepperPepper.IRSTD.datasets import DataSetLoader
from PepperPepper.IRSTD.tools.metrics import SegmentationMetricTPFNFP
from PepperPepper.IRSTD.models import IRSTDNet



def get_IRSTDtrain_config():
    config = ml_collections.ConfigDict()
    config.model_name = 'MiM'
    config.dataset_name = 'NUDT-SIRST'
    config.dataset_dir = './datasets'
    config.optimizer = 'Adam'
    config.lr_scheduler = 'CosineAnnealingLR'
    config.lr = 1e-3
    config.lr_min = 1e-5
    config.epochs = 600
    config.batch_size = 8
    config.img_size = 256
    config.save = './results'
    config.img_norm_cfg = None

    config.seed = 42

    # config.resume = False

    current_time = time.localtime()
    config.time = time.strftime("%Y-%m-%d-%H.%M.%S", current_time)
    config.title = 'train'

    # config.save_path = os.path.join(config.save, config.model_name, config.dataset_name, config.title + '_' + config.time)

    return config


class IRSTDTrainer:
    def __init__(self, config, device=None):
        """
        初始化 Trainer 类

        Args:
            model (torch.nn.Module): 要训练的模型
            loss_fn (callable): 损失函数
            optimizer (torch.optim.Optimizer): 优化器
            lr_scheduler (torch.optim.lr_scheduler, optional): 学习率调度器，默认为 None
            device (str or torch.device, optional): 设备 ('cuda' 或 'cpu')，默认为自动检测
            ml_collect (dict, optional): 额外的参数配置字典，用于自定义行为
        """

        ## train parameter
        self.config = config
        self.seed_pytorch(config.seed)
        self.net = IRSTDNet(config.model_name)
        self.loss_fn = self.net.loss
        self.optimizer = self.get_optimizer()
        self.lr_scheduler = self.get_scheduler()
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.net.to(self.device)

        train_set = DataSetLoader(config.dataset_dir, config.dataset_name, config.img_size, mode='train')
        test_set = DataSetLoader(config.dataset_dir, config.dataset_name, config.img_size, mode='test')

        self.train_loader = DataLoader(dataset=train_set, batch_size=config.batch_size, shuffle=True)
        self.test_loader = DataLoader(dataset=test_set, batch_size=config.batch_size, shuffle=True)


        self.metrics = SegmentationMetricTPFNFP(nclass=1)
        self.best_miou = 0
        self.fmeasure = 0
        self.prec = 0
        self.recall = 0


        ## save_path

        self.save_path = os.path.join(config.save, config.model_name, config.dataset_name, config.title + '_' + config.time)
        self.epoch = 0
        self.writer = None
        self.file_path = os.path.join(self.save_path, f"log_ling.txt")







    def train(self, epochs = None):
        # setting epoch
        if epochs is None:
            try:
                epochs = self.config.epochs
            except:
                epochs = 600


        print('IRSTD Net:{} Dataset:{} Start training...'.format(self.config.model_name, self.config.dataset_name))
        print(self.config)
        # tbar = tqdm.tqdm(self.train_loader)

        for idx_epoch in range(epochs):
            all_loss = []
            self.net.train()
            self.epoch = idx_epoch + 1
            tbar = tqdm.tqdm(self.train_loader)

            for idx_iter ,(img , mask) in enumerate(tbar):
                img = img.to(self.device)
                mask = mask.to(self.device)

                preds = self.net(img)
                loss = self.loss_fn(preds, mask)


                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

                all_loss.append(loss.detach().cpu())
                tbar.set_description('Train Epoch {}/{}, loss {}, lr {:.6f}/{:.6f}-{:.6f}'.format(self.epoch, epochs, loss.item(), self.optimizer.param_groups[0]['lr'], self.config.lr, self.config.lr_min))


            if self.lr_scheduler is not None:
                self.lr_scheduler.step()

            log_loss = float(np.array(all_loss).mean())
            self.check_dir(self.save_path)




            if self.writer is None:
                self.writer = SummaryWriter(os.path.join(self.save_path, 'log'))
            else:
                self.writer.add_scalar('train loss', log_loss, self.epoch)
                self.writer.add_scalar('train lr', self.optimizer.param_groups[0]['lr'], self.epoch)
            with open(self.file_path, 'a+') as f:
                # 写入一些记录
                f.write('Train Epoch {}/{}, loss {}, lr {:.6f}/{:.6f}-{:.6f}\n'.format(idx_epoch + 1, epochs, loss.item(), self.optimizer.param_groups[0]['lr'], self.config.lr, self.config.lr_min))
                # 刷新缓冲区，确保写入的数据立即保存到文件
                f.flush()





            self.test()




    def test(self):
        tbar = tqdm.tqdm(self.test_loader)
        self.metrics.reset()
        self.net.eval()

        with torch.no_grad():
            for idx_iter ,(img , mask) in enumerate(tbar):
                img = img.to(self.device)
                mask = mask.to(self.device)
                pred = self.net(img)
                if isinstance(pred, tuple):
                    pred = pred[-1]
                elif isinstance(pred, list):
                    pred = pred[-1]
                else:
                    pred = pred

                # loss = self.loss_fn(pred, mask)

                self.metrics.update(mask.cpu(), pred.cpu())

                miou, prec, recall, fmeasure = self.metrics.get()

                tbar.set_description('Test Epoch {}/{}, miou {:.6f}/{:.6f}, F1 {:.6f}/{:.6f}'.format(self.epoch, self.config.epochs, miou, self.best_miou, fmeasure, self.fmeasure))

            miou, prec, recall, fmeasure = self.metrics.get()


            if self.writer is None:
                self.writer = SummaryWriter(os.path.join(self.save_path, 'log'))
            else:
                self.writer.add_scalar('test mIOU', miou, self.epoch)

            with open(self.file_path, 'a+') as f:
                # 写入一些记录
                f.write('Test Epoch {}/{}, miou {:.6f}/{:.6f}, F1 {:.6f}/{:.6f}\n'.format(self.epoch, self.config.epochs, miou, self.best_miou, fmeasure, self.fmeasure))
                # 刷新缓冲区，确保写入的数据立即保存到文件
                f.flush()

            if miou > self.best_miou:
                self.best_miou = miou
                self.prec = prec
                self.recall = recall
                self.fmeasure = fmeasure


                self.save_model(title='best')
                ## save net





    def get_optimizer(self, config=None):
        if config is None:
            config = self.config

        if config.optimizer == 'Adam':
            optimizer = torch.optim.Adam(self.net.parameters(), lr=config.lr)
        else:
            raise NotImplementedError('Not implemented optimizer')

        return optimizer


    def get_scheduler(self, config=None):
        if config is None:
            config = self.config

        if config.lr_scheduler == 'CosineAnnealingLR':
            scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(self.optimizer, config.epochs, eta_min=config.lr_min)
        else:
            return None

        return scheduler





    def save_model(self, title, save_path = None):
        if save_path is None:
            save_path = self.save_path

        self.check_dir(save_path)

        checkpoint = {
            'config':self.config,
            'model_state_dict':self.net.state_dict(),
            'optimizer_state_dict':self.optimizer.state_dict(),
            'scheduler_state_dict': self.lr_scheduler.state_dict(),  # 学习率调度器参数
            'epoch': self.epoch,  # 当前 epoch
            'best_miou':self.best_miou,
            'lr':self.optimizer.param_groups[0]['lr']  # 当前学习率,
        }

        torch.save(checkpoint,os.path.join(save_path, title))

        with open(self.file_path, 'a+') as f:
            # 写入一些记录
            f.write('--- Save {} Model\n'.format(title))
            f.write('--- epoch:{}, best_miou:{:.6f}, prec:{:.6f} , recall:{:.6f}, fmeasure:{:.6f}\n'.format(self.epoch+1, self.best_miou, self.prec, self.recall, self.fmeasure))
            # 刷新缓冲区，确保写入的数据立即保存到文件
            f.flush()


        print('--- Save {} Model'.format(title))
        print('--- epoch:{}, best_miou:{:.6f}, prec:{:.6f} , recall:{:.6f}, fmeasure:{:.6f}'.format(self.epoch+1, self.best_miou, self.prec, self.recall, self.fmeasure))



    # 加载模型和训练状态
    def load_checkpoint(self, model, optimizer, scheduler, save_path):
        checkpoint = torch.load(save_path)
        self.config = checkpoint['config']
        self.net.load_state_dict(checkpoint['model_state_dict'])  # 加载模型参数
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])  # 加载优化器参数
        self.lr_scheduler.load_state_dict(checkpoint['scheduler_state_dict'])  # 加载调度器参数
        self.epoch = checkpoint['epoch']  # 恢复 epoch
        self.best_miou = checkpoint['best_miou']  # 恢复最佳 IoU
        self.lr = checkpoint['lr']  # 恢复学习率
        print(f"Checkpoint loaded from {save_path}")


    def check_dir(self, path):
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            print(f"Directory '{path}' created.")

    def seed_pytorch(self, seed=42):
        random.seed(seed)
        os.environ['PYTHONHASHSEED'] = str(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)

