package com.movie.nbspringproduct.controller;

import com.movie.nbspringproduct.common.Result;
import com.movie.nbspringproduct.entity.NbAllowancePolicy;
import com.movie.nbspringproduct.entity.NbCreditLoan;
import com.movie.nbspringproduct.entity.NbFarmProduce;
import com.movie.nbspringproduct.entity.NbFarmMarket;
import com.movie.nbspringproduct.entity.NbGraphicCourse;
import com.movie.nbspringproduct.entity.NbVideoCourse;
import com.movie.nbspringproduct.service.INbAllowancePolicyService;
import com.movie.nbspringproduct.service.INbCreditLoanService;
import com.movie.nbspringproduct.service.INbFarmProduceService;
import com.movie.nbspringproduct.service.INbFarmMarketService;
import com.movie.nbspringproduct.service.INbGraphicCourseService;
import com.movie.nbspringproduct.service.INbVideoCourseService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.math.BigDecimal;
import java.text.SimpleDateFormat;
import java.util.Date;

/**
 * 数据初始化Controller - 用于导入农业助农测试数据
 */
@RestController
@RequestMapping("/dev-api/init")
public class DataInitController {
    
    @Autowired
    private INbAllowancePolicyService policyService;
    
    @Autowired
    private INbCreditLoanService loanService;
    
    @Autowired
    private INbFarmProduceService produceService;
    
    @Autowired
    private INbFarmMarketService marketService;
    
    @Autowired
    private INbGraphicCourseService graphicCourseService;
    
    @Autowired
    private INbVideoCourseService videoCourseService;
    
    /**
     * 初始化所有农业助农数据
     * 访问地址：http://localhost:8081/dev-api/init/data
     */
    @GetMapping("/data")
    public Result<String> initData() {
        try {
            // 清空现有数据（可选）
            // policyService.remove(null);
            
            // 1. 插入农业补贴政策数据
            insertPolicyData();
            
            // 2. 插入农业信贷信息数据
            insertLoanData();
            
            // 3. 插入农产品数据
            insertProduceData();
            
            // 4. 插入农贸市场数据
            insertMarketData();
            
            // 5. 插入图文课程数据
            insertGraphicCourseData();
            
            // 6. 插入视频课程数据
            insertVideoCourseData();
            
            return Result.success("农业助农数据初始化成功！共插入：5条补贴政策、4条信贷信息、5条农产品信息、10条农贸市场信息、5条图文课程、5条视频课程");
        } catch (Exception e) {
            e.printStackTrace();
            return Result.error("数据初始化失败：" + e.getMessage());
        }
    }
    
    /**
     * 单独初始化农贸市场数据
     * 访问地址：http://localhost:8081/dev-api/init/market
     */
    @GetMapping("/market")
    public Result<String> initMarketData() {
        try {
            insertMarketData();
            return Result.success("农贸市场数据初始化成功！共插入10条市场信息");
        } catch (Exception e) {
            e.printStackTrace();
            return Result.error("农贸市场数据初始化失败：" + e.getMessage());
        }
    }
    
    /**
     * 插入农业补贴政策数据
     */
    private void insertPolicyData() {
        // 1. 粮食种植补贴
        NbAllowancePolicy policy1 = new NbAllowancePolicy();
        policy1.setTitle("2025年粮食种植补贴政策");
        policy1.setAuthor("农业农村部");
        policy1.setResume("对种植水稻、小麦、玉米等粮食作物的农户给予每亩补贴");
        policy1.setContent("为保障国家粮食安全，鼓励农民种粮积极性，对种植水稻、小麦、玉米等粮食作物的农户，按照实际种植面积给予每亩200元的直接补贴。补贴资金由中央财政和地方财政共同承担，确保及时足额发放到农户手中。");
        policy1.setBrowseNum(150);
        policy1.setPublishStatus(1);
        policy1.setPublishTime(new Date());
        policy1.setRecommend(1);
        policyService.save(policy1);
        
        // 2. 农机购置补贴
        NbAllowancePolicy policy2 = new NbAllowancePolicy();
        policy2.setTitle("农机购置补贴实施方案");
        policy2.setAuthor("农业农村部");
        policy2.setResume("购买农业机械设备可享受30%-50%的补贴");
        policy2.setContent("为推动农业机械化发展，对购买拖拉机、收割机、播种机、植保无人机等农业机械的农户和农业合作社，给予购置价格30%-50%的财政补贴。单户年度补贴总额不超过30万元。");
        policy2.setBrowseNum(200);
        policy2.setPublishStatus(1);
        policy2.setPublishTime(new Date());
        policy2.setRecommend(1);
        policyService.save(policy2);
        
        // 3. 设施农业补助
        NbAllowancePolicy policy3 = new NbAllowancePolicy();
        policy3.setTitle("设施农业建设补助政策");
        policy3.setAuthor("农业农村部");
        policy3.setResume("建设温室大棚、智能养殖场等可获得补助");
        policy3.setContent("支持发展现代设施农业，对新建或改造温室大棚、智能养殖场、冷链仓储设施等项目，按照投资额度给予20%-40%的财政补助。单个项目补助金额最高不超过100万元。");
        policy3.setBrowseNum(120);
        policy3.setPublishStatus(1);
        policy3.setPublishTime(new Date());
        policy3.setRecommend(0);
        policyService.save(policy3);
        
        // 4. 农业保险补贴
        NbAllowancePolicy policy4 = new NbAllowancePolicy();
        policy4.setTitle("农业保险补贴政策");
        policy4.setAuthor("财政部、农业农村部");
        policy4.setResume("农户购买农业保险可享受保费补贴");
        policy4.setContent("为降低农业生产风险，对农户购买种植业、养殖业保险，中央和地方财政给予保费50%-80%的补贴支持。包括水稻、小麦、玉米、大豆等主要粮食作物保险和生猪、奶牛等畜牧业保险。");
        policy4.setBrowseNum(180);
        policy4.setPublishStatus(1);
        policy4.setPublishTime(new Date());
        policy4.setRecommend(1);
        policyService.save(policy4);
        
        // 5. 乡村振兴补贴
        NbAllowancePolicy policy5 = new NbAllowancePolicy();
        policy5.setTitle("乡村振兴产业发展补贴");
        policy5.setAuthor("国家乡村振兴局");
        policy5.setResume("发展特色农业产业可申请专项资金支持");
        policy5.setContent("支持乡村特色产业发展，对发展特色种植、养殖、加工、乡村旅游等产业项目，可申请10-50万元的专项资金支持。重点支持一村一品、农产品加工、电商物流等项目。");
        policy5.setBrowseNum(95);
        policy5.setPublishStatus(0);
        policy5.setRecommend(0);
        policyService.save(policy5);
    }
    
    /**
     * 插入农业信贷信息数据
     */
    private void insertLoanData() {
        // 1. 农户小额信用贷款
        NbCreditLoan loan1 = new NbCreditLoan();
        loan1.setTitle("农户小额信用贷款");
        loan1.setAuthor("农业银行");
        loan1.setResume("无需抵押，最高可贷30万元");
        loan1.setContent("专为农户设计的小额信用贷款产品，凭借良好信用记录即可申请，无需抵押担保，贷款额度最高30万元，年化利率4.5%-5.5%，用于农业生产经营、购买农资、农机等。申请便捷，当天审批，快速放款。");
        loan1.setImage("/images/loan1.jpg");
        loan1.setBrowseNum(300);
        loan1.setPublishStatus(1);
        loan1.setPublishTime(new Date());
        loan1.setRecommend(1);
        loanService.save(loan1);
        
        // 2. 新型农业经营主体贷款
        NbCreditLoan loan2 = new NbCreditLoan();
        loan2.setTitle("新型农业经营主体贷款");
        loan2.setAuthor("农业银行");
        loan2.setResume("家庭农场、合作社专属贷款产品");
        loan2.setContent("面向家庭农场、农民合作社、农业企业等新型农业经营主体，提供最高500万元的信贷支持，利率优惠，用于扩大生产规模、购置设备、土地流转等。支持线上申请，手续简便。");
        loan2.setImage("/images/loan2.jpg");
        loan2.setBrowseNum(250);
        loan2.setPublishStatus(1);
        loan2.setPublishTime(new Date());
        loan2.setRecommend(1);
        loanService.save(loan2);
        
        // 3. 农业产业链金融
        NbCreditLoan loan3 = new NbCreditLoan();
        loan3.setTitle("农业产业链金融服务");
        loan3.setAuthor("邮储银行");
        loan3.setResume("全产业链金融支持方案");
        loan3.setContent("针对农业产业链上下游企业，提供种植、加工、流通、销售全链条的金融服务。单户最高1000万元授信额度，灵活的还款方式，支持订单融资、应收账款融资等多种模式。");
        loan3.setImage("/images/loan3.jpg");
        loan3.setBrowseNum(180);
        loan3.setPublishStatus(1);
        loan3.setPublishTime(new Date());
        loan3.setRecommend(0);
        loanService.save(loan3);
        
        // 4. 乡村创业担保贷款
        NbCreditLoan loan4 = new NbCreditLoan();
        loan4.setTitle("乡村创业担保贷款");
        loan4.setAuthor("人社部、财政部");
        loan4.setResume("返乡创业可享受贴息贷款");
        loan4.setContent("支持返乡农民工、大学生、退役军人等人员在农村创业，提供最高50万元的创业担保贷款，财政给予全额贴息，降低创业成本。用于农产品加工、电商、乡村旅游等创业项目。");
        loan4.setImage("/images/loan4.jpg");
        loan4.setBrowseNum(220);
        loan4.setPublishStatus(0);
        loan4.setRecommend(1);
        loanService.save(loan4);
    }
    
    /**
     * 插入农产品数据
     */
    private void insertProduceData() {
        // 1. 有机大米
        NbFarmProduce produce1 = new NbFarmProduce();
        produce1.setTitle("有机大米");
        produce1.setResume("东北黑土地优质大米");
        produce1.setDescription("来自东北黑土地的有机大米，无化肥无农药，全程有机种植，口感香糯，营养丰富，富含多种维生素和矿物质。5公斤精品装。");
        produce1.setImage("/images/rice.jpg");
        produce1.setCatgory("粮食");
        produce1.setProduceType("有机");
        produce1.setPrice(new BigDecimal("15.80"));
        produce1.setBrowseNum(500);
        produce1.setPushStatus(1);
        produce1.setPushTime(new Date());
        produce1.setRecommend(1);
        produce1.setProviderName("黑龙江绿色农场");
        produceService.save(produce1);
        
        // 2. 新鲜蔬菜
        NbFarmProduce produce2 = new NbFarmProduce();
        produce2.setTitle("新鲜蔬菜礼盒");
        produce2.setResume("当季时令蔬菜组合");
        produce2.setDescription("精选当季新鲜蔬菜，包含西红柿、黄瓜、青菜、茄子等10种蔬菜，农场直供，当天采摘当天配送，新鲜美味，绿色健康。");
        produce2.setImage("/images/vegetables.jpg");
        produce2.setCatgory("蔬菜");
        produce2.setProduceType("绿色");
        produce2.setPrice(new BigDecimal("38.00"));
        produce2.setBrowseNum(450);
        produce2.setPushStatus(1);
        produce2.setPushTime(new Date());
        produce2.setRecommend(1);
        produce2.setProviderName("阳光蔬菜基地");
        produceService.save(produce2);
        
        // 3. 散养土鸡蛋
        NbFarmProduce produce3 = new NbFarmProduce();
        produce3.setTitle("散养土鸡蛋");
        produce3.setResume("农家散养土鸡蛋");
        produce3.setDescription("山区散养土鸡所产，鸡只自由觅食，食用天然谷物和虫草，蛋黄金黄饱满，营养价值高，富含卵磷脂。30枚精品装。");
        produce3.setImage("/images/eggs.jpg");
        produce3.setCatgory("禽蛋");
        produce3.setProduceType("散养");
        produce3.setPrice(new BigDecimal("45.00"));
        produce3.setBrowseNum(600);
        produce3.setPushStatus(1);
        produce3.setPushTime(new Date());
        produce3.setRecommend(1);
        produce3.setProviderName("山里人家养殖场");
        produceService.save(produce3);
        
        // 4. 红富士苹果
        NbFarmProduce produce4 = new NbFarmProduce();
        produce4.setTitle("烟台红富士苹果");
        produce4.setResume("山东烟台特产苹果");
        produce4.setDescription("山东烟台特产红富士苹果，果大色艳，脆甜多汁，富含维生素C和膳食纤维。精选果径80mm以上优质果，5斤礼盒装。");
        produce4.setImage("/images/apple.jpg");
        produce4.setCatgory("水果");
        produce4.setProduceType("绿色");
        produce4.setPrice(new BigDecimal("29.90"));
        produce4.setBrowseNum(380);
        produce4.setPushStatus(1);
        produce4.setPushTime(new Date());
        produce4.setRecommend(0);
        produce4.setProviderName("烟台果园");
        produceService.save(produce4);
        
        // 5. 明前龙井茶
        NbFarmProduce produce5 = new NbFarmProduce();
        produce5.setTitle("明前龙井茶");
        produce5.setResume("杭州西湖龙井茶");
        produce5.setDescription("杭州西湖龙井明前茶，清明前采摘的嫩芽，香气浓郁，回味甘甜，茶汤清澈明亮。传统手工炒制，保留天然茶香。250克精装礼盒。");
        produce5.setImage("/images/tea.jpg");
        produce5.setCatgory("茶叶");
        produce5.setProduceType("有机");
        produce5.setPrice(new BigDecimal("168.00"));
        produce5.setBrowseNum(280);
        produce5.setPushStatus(0);
        produce5.setRecommend(1);
        produce5.setProviderName("西湖茶庄");
        produceService.save(produce5);
    }
    
    /**
     * 插入农贸市场数据
     */
    private void insertMarketData() throws Exception {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        
        // 1. 绿色农贸批发市场
        NbFarmMarket market1 = new NbFarmMarket();
        market1.setName("绿色农贸批发市场");
        market1.setRegionId("城市-朝阳区");
        market1.setRemark("主营蔬菜、水果、粮油等农产品批发，日均客流量3000+人次，设有200个固定摊位");
        market1.setCreateTime(sdf.parse("2024-01-15 09:30:00"));
        marketService.save(market1);
        
        // 2. 鲜果集市
        NbFarmMarket market2 = new NbFarmMarket();
        market2.setName("鲜果集市");
        market2.setRegionId("城市-海淀区");
        market2.setRemark("专业水果批发市场，提供国内外优质水果，冷链物流配送，日吞吐量50吨");
        market2.setCreateTime(sdf.parse("2024-02-20 14:20:00"));
        marketService.save(market2);
        
        // 3. 田园综合市场
        NbFarmMarket market3 = new NbFarmMarket();
        market3.setName("田园综合市场");
        market3.setRegionId("郊区-顺义区");
        market3.setRemark("集农产品交易、仓储、加工于一体的综合性市场，占地面积20000平方米");
        market3.setCreateTime(sdf.parse("2024-03-10 08:00:00"));
        marketService.save(market3);
        
        // 4. 有机蔬菜交易中心
        NbFarmMarket market4 = new NbFarmMarket();
        market4.setName("有机蔬菜交易中心");
        market4.setRegionId("郊区-大兴区");
        market4.setRemark("专注有机绿色蔬菜交易，所有产品经过严格检测认证，服务周边5个区县");
        market4.setCreateTime(sdf.parse("2024-04-05 10:15:00"));
        marketService.save(market4);
        
        // 5. 畜禽产品批发市场
        NbFarmMarket market5 = new NbFarmMarket();
        market5.setName("畜禽产品批发市场");
        market5.setRegionId("城市-丰台区");
        market5.setRemark("肉类、禽蛋专业批发市场，具备完善的冷藏设施，日交易额达100万元");
        market5.setCreateTime(sdf.parse("2024-05-18 07:45:00"));
        marketService.save(market5);
        
        // 6. 水产海鲜大市场
        NbFarmMarket market6 = new NbFarmMarket();
        market6.setName("水产海鲜大市场");
        market6.setRegionId("城市-石景山区");
        market6.setRemark("各类水产品、海鲜批发零售，活鱼池50余个，日供应新鲜水产10吨以上");
        market6.setCreateTime(sdf.parse("2024-06-12 11:30:00"));
        marketService.save(market6);
        
        // 7. 粮油调味品批发中心
        NbFarmMarket market7 = new NbFarmMarket();
        market7.setName("粮油调味品批发中心");
        market7.setRegionId("郊区-通州区");
        market7.setRemark("各类粮油、调味品、干货批发，仓储面积15000平方米，辐射京津冀地区");
        market7.setCreateTime(sdf.parse("2024-07-22 09:00:00"));
        marketService.save(market7);
        
        // 8. 农副产品综合市场
        NbFarmMarket market8 = new NbFarmMarket();
        market8.setName("农副产品综合市场");
        market8.setRegionId("城市-东城区");
        market8.setRemark("综合性农副产品市场，品类齐全，价格实惠，日均交易量80吨");
        market8.setCreateTime(sdf.parse("2024-08-30 13:20:00"));
        marketService.save(market8);
        
        // 9. 特色农产品展销中心
        NbFarmMarket market9 = new NbFarmMarket();
        market9.setName("特色农产品展销中心");
        market9.setRegionId("郊区-昌平区");
        market9.setRemark("汇集全国各地特色农产品，定期举办农产品展销会，年交易额超5000万元");
        market9.setCreateTime(sdf.parse("2024-09-14 15:10:00"));
        marketService.save(market9);
        
        // 10. 社区便民菜市场
        NbFarmMarket market10 = new NbFarmMarket();
        market10.setName("社区便民菜市场");
        market10.setRegionId("城市-西城区");
        market10.setRemark("服务周边10个社区，提供新鲜蔬菜水果、肉类、粮油等生活必需品");
        market10.setCreateTime(sdf.parse("2024-10-08 08:30:00"));
        marketService.save(market10);
    }
    
    /**
     * 插入图文课程数据
     */
    private void insertGraphicCourseData() {
        // 1. 水稻种植技术指南
        NbGraphicCourse course1 = new NbGraphicCourse();
        course1.setTitle("水稻种植技术指南");
        course1.setTeacher("李教授");
        course1.setResume("详细介绍水稻从育秧到收获的全过程种植技术");
        course1.setContent("本课程系统讲解水稻种植的关键技术要点，包括品种选择、育秧管理、田间管理、病虫害防治等内容。");
        course1.setImage("/images/course/rice.jpg");
        course1.setCategory("种植技术");
        course1.setBrowseNum(156);
        course1.setPublishStatus(1);
        course1.setPublishTime(new Date());
        course1.setRecommend(1);
        graphicCourseService.save(course1);
        
        // 2. 有机蔬菜栽培技术
        NbGraphicCourse course2 = new NbGraphicCourse();
        course2.setTitle("有机蔬菜栽培技术");
        course2.setTeacher("王老师");
        course2.setResume("从零开始学习有机蔬菜种植的实用技术");
        course2.setContent("课程涵盖有机蔬菜的土壤准备、种子处理、田间管理、病虫害生物防治等核心内容。");
        course2.setImage("/images/course/vegetables.jpg");
        course2.setCategory("种植技术");
        course2.setBrowseNum(203);
        course2.setPublishStatus(1);
        course2.setPublishTime(new Date());
        course2.setRecommend(1);
        graphicCourseService.save(course2);
        
        // 3. 果树修剪与管理
        NbGraphicCourse course3 = new NbGraphicCourse();
        course3.setTitle("果树修剪与管理");
        course3.setTeacher("张专家");
        course3.setResume("掌握果树修剪的方法和技巧，提高果实品质");
        course3.setContent("详细讲解苹果、梨、桃等常见果树的修剪时期、修剪方法和注意事项。");
        course3.setImage("/images/course/fruit-tree.jpg");
        course3.setCategory("果树管理");
        course3.setBrowseNum(178);
        course3.setPublishStatus(1);
        course3.setPublishTime(new Date());
        course3.setRecommend(0);
        graphicCourseService.save(course3);
        
        // 4. 农业病虫害识别与防治
        NbGraphicCourse course4 = new NbGraphicCourse();
        course4.setTitle("农业病虫害识别与防治");
        course4.setTeacher("陈老师");
        course4.setResume("学会识别常见农业病虫害，掌握科学防治方法");
        course4.setContent("课程包含水稻、小麦、玉米等作物的主要病虫害识别特征及综合防治策略。");
        course4.setImage("/images/course/pest-control.jpg");
        course4.setCategory("病虫害防治");
        course4.setBrowseNum(245);
        course4.setPublishStatus(1);
        course4.setPublishTime(new Date());
        course4.setRecommend(1);
        graphicCourseService.save(course4);
        
        // 5. 智慧农业技术应用
        NbGraphicCourse course5 = new NbGraphicCourse();
        course5.setTitle("智慧农业技术应用");
        course5.setTeacher("刘博士");
        course5.setResume("了解现代农业技术在生产中的应用");
        course5.setContent("介绍物联网、大数据、人工智能等技术在农业生产中的具体应用案例。");
        course5.setImage("/images/course/smart-farm.jpg");
        course5.setCategory("智慧农业");
        course5.setBrowseNum(189);
        course5.setPublishStatus(1);
        course5.setPublishTime(new Date());
        course5.setRecommend(0);
        graphicCourseService.save(course5);
    }
    
    /**
     * 插入视频课程数据
     */
    private void insertVideoCourseData() {
        // 1. 小麦高产栽培技术
        NbVideoCourse course1 = new NbVideoCourse();
        course1.setTitle("小麦高产栽培技术");
        course1.setTeacher("赵教授");
        course1.setResume("视频讲解小麦高产栽培的关键技术措施");
        course1.setContent("本视频课程从品种选择、播种技术、肥水管理、病虫害防治等方面全面介绍小麦高产栽培技术。");
        course1.setImage("/images/course/wheat.jpg");
        course1.setVideoUrl("/videos/wheat-cultivation.mp4");
        course1.setDuration("45分钟");
        course1.setCategory("种植技术");
        course1.setBrowseNum(312);
        course1.setPublishStatus(1);
        course1.setPublishTime(new Date());
        course1.setRecommend(1);
        videoCourseService.save(course1);
        
        // 2. 温室大棚建设与管理
        NbVideoCourse course2 = new NbVideoCourse();
        course2.setTitle("温室大棚建设与管理");
        course2.setTeacher("孙工程师");
        course2.setResume("手把手教你建设和管理温室大棚");
        course2.setContent("详细演示温室大棚的选址、建设流程、设备安装、日常管理等实操内容。");
        course2.setImage("/images/course/greenhouse.jpg");
        course2.setVideoUrl("/videos/greenhouse-setup.mp4");
        course2.setDuration("52分钟");
        course2.setCategory("设施农业");
        course2.setBrowseNum(267);
        course2.setPublishStatus(1);
        course2.setPublishTime(new Date());
        course2.setRecommend(1);
        videoCourseService.save(course2);
        
        // 3. 畜禽养殖技术
        NbVideoCourse course3 = new NbVideoCourse();
        course3.setTitle("畜禽养殖技术");
        course3.setTeacher("吴专家");
        course3.setResume("科学养殖技术，提高养殖效益");
        course3.setContent("涵盖猪、鸡、牛等常见畜禽的品种选择、饲养管理、疾病防控等实用技术。");
        course3.setImage("/images/course/livestock.jpg");
        course3.setVideoUrl("/videos/livestock-farming.mp4");
        course3.setDuration("38分钟");
        course3.setCategory("养殖技术");
        course3.setBrowseNum(198);
        course3.setPublishStatus(1);
        course3.setPublishTime(new Date());
        course3.setRecommend(0);
        videoCourseService.save(course3);
        
        // 4. 农产品电商营销
        NbVideoCourse course4 = new NbVideoCourse();
        course4.setTitle("农产品电商营销");
        course4.setTeacher("周老师");
        course4.setResume("学习农产品线上销售的方法和技巧");
        course4.setContent("从平台选择、店铺运营、产品包装、物流配送等角度讲解农产品电商营销策略。");
        course4.setImage("/images/course/ecommerce.jpg");
        course4.setVideoUrl("/videos/ecommerce-marketing.mp4");
        course4.setDuration("41分钟");
        course4.setCategory("经营管理");
        course4.setBrowseNum(234);
        course4.setPublishStatus(1);
        course4.setPublishTime(new Date());
        course4.setRecommend(1);
        videoCourseService.save(course4);
        
        // 5. 农业机械使用与维护
        NbVideoCourse course5 = new NbVideoCourse();
        course5.setTitle("农业机械使用与维护");
        course5.setTeacher("郑技师");
        course5.setResume("掌握常用农业机械的操作和维护技能");
        course5.setContent("视频演示拖拉机、收割机、植保机等农业机械的正确使用方法和日常维护保养。");
        course5.setImage("/images/course/machinery.jpg");
        course5.setVideoUrl("/videos/machinery-maintenance.mp4");
        course5.setDuration("36分钟");
        course5.setCategory("农机技术");
        course5.setBrowseNum(176);
        course5.setPublishStatus(1);
        course5.setPublishTime(new Date());
        course5.setRecommend(0);
        videoCourseService.save(course5);
    }
    
    /**
     * 单独初始化课程数据
     * 访问地址：http://localhost:8081/dev-api/init/course
     */
    @GetMapping("/course")
    public Result<String> initCourseData() {
        try {
            insertGraphicCourseData();
            insertVideoCourseData();
            return Result.success("课程数据初始化成功！共插入5条图文课程、5条视频课程");
        } catch (Exception e) {
            e.printStackTrace();
            return Result.error("课程数据初始化失败：" + e.getMessage());
        }
    }
}

