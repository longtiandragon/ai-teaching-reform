package org.nong.controller;

import org.nong.common.Result;
import org.nong.mapper.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.*;

/**
 * 统计数据Controller
 */
@RestController
@RequestMapping("/api/statistics")
@CrossOrigin(originPatterns = "*", allowCredentials = "true")
public class StatisticsController {

    @Autowired
    private NbFarmProduceMapper produceMapper;
    
    @Autowired
    private NbExpertMapper expertMapper;
    
    @Autowired
    private NbCreditLoanMapper loanMapper;
    
    @Autowired
    private NbServiceMapper serviceMapper;

    /**
     * 获取概览数据
     */
    @GetMapping("/overview")
    public Result<Map<String, Object>> getOverview() {
        try {
            Map<String, Object> overview = new HashMap<>();
            
            // 获取补贴政策总数（模拟数据）
            overview.put("policyCount", 0);
            
            // 获取信贷产品总数
            Long loanCount = loanMapper.selectCount(new HashMap<>());
            overview.put("loanCount", loanCount != null ? loanCount : 0);
            
            // 获取农产品总数
            Long produceCount = produceMapper.selectCount(new HashMap<>());
            overview.put("produceCount", produceCount != null ? produceCount : 0);
            
            // 获取总浏览量（模拟数据）
            overview.put("totalViews", 0);
            
            return Result.success(overview);
        } catch (Exception e) {
            e.printStackTrace();
            return Result.error("获取概览数据失败");
        }
    }

    /**
     * 获取产品销量数据
     */
    @GetMapping("/productStats")
    public Result<Map<String, Object>> getProductStats() {
        try {
            System.out.println("📊 开始获取产品销量数据...");
            Map<String, Object> stats = new HashMap<>();
            
            // 获取所有农产品
            List products = produceMapper.selectList(new HashMap<>());
            System.out.println("📦 数据库查询结果: " + (products == null ? "null" : products.size() + "条"));
            
            List<Map<String, Object>> salesData = new ArrayList<>();
            
            // 如果数据库中没有数据，生成模拟数据
            if (products == null || products.isEmpty()) {
                System.out.println("⚠️ 数据库无数据，生成模拟数据...");
                // 生成6个模拟产品数据
                String[] productNames = {"有机蔬菜", "优质水稻", "生态水果", "绿色茶叶", "特色杂粮", "精品菌菇"};
                for (String name : productNames) {
                    Map<String, Object> item = new HashMap<>();
                    item.put("name", name);
                    item.put("sales", (int)(Math.random() * 40) + 10);
                    item.put("browse", (int)(Math.random() * 400) + 100);
                    salesData.add(item);
                }
                System.out.println("✅ 生成了 " + salesData.size() + " 条模拟数据");
            } else {
                // 限制只显示前10个产品
                int count = 0;
                for (Object obj : products) {
                    if (count >= 10) break;
                    
                    try {
                        // 使用反射获取字段值
                        java.lang.reflect.Method getTitleMethod = obj.getClass().getMethod("getTitle");
                        java.lang.reflect.Method getBrowseNumMethod = obj.getClass().getMethod("getBrowseNum");
                        
                        String title = (String) getTitleMethod.invoke(obj);
                        Integer browseValue = (Integer) getBrowseNumMethod.invoke(obj);
                        
                        Map<String, Object> item = new HashMap<>();
                        item.put("name", title != null ? title : "未知产品");
                        // 农产品没有销量字段，用浏览量的一半模拟销量
                        int browse = (browseValue != null && browseValue > 0) ? browseValue : (int)(Math.random() * 400) + 100;
                        int sales = browse / 10; // 销量约为浏览量的1/10
                        
                        item.put("sales", sales);
                        item.put("browse", browse);
                        
                        salesData.add(item);
                        count++;
                        System.out.println("✅ 添加产品: " + title + ", 销量:" + sales + ", 浏览:" + browse);
                    } catch (Exception e) {
                        System.err.println("❌ 反射错误: " + e.getMessage());
                        e.printStackTrace();
                    }
                }
            }
            
            stats.put("salesData", salesData);
            System.out.println("✅ 最终返回数据: salesData.size=" + salesData.size());
            System.out.println("📤 返回数据详情: " + stats);
            
            return Result.success(stats);
        } catch (Exception e) {
            System.err.println("❌ 获取产品销量数据异常:");
            e.printStackTrace();
            return Result.error("获取销量数据失败");
        }
    }

    /**
     * 获取产品分布数据
     */
    @GetMapping("/distribution")
    public Result<Map<String, Object>> getDistribution() {
        try {
            Map<String, Object> result = new HashMap<>();
            List<Map<String, Object>> categoryData = new ArrayList<>();
            
            // 获取各类产品数量
            Long produceCount = produceMapper.selectCount(new HashMap<>());
            Long expertCount = expertMapper.selectCount(new HashMap<>());
            Long loanCount = loanMapper.selectCount(new HashMap<>());
            Long serviceCount = serviceMapper.selectCount(new HashMap<>());
            
            Map<String, Object> produce = new HashMap<>();
            produce.put("name", "农产品");
            produce.put("value", produceCount != null ? produceCount : 0);
            categoryData.add(produce);
            
            Map<String, Object> expert = new HashMap<>();
            expert.put("name", "专家");
            expert.put("value", expertCount != null ? expertCount : 0);
            categoryData.add(expert);
            
            Map<String, Object> loan = new HashMap<>();
            loan.put("name", "信贷产品");
            loan.put("value", loanCount != null ? loanCount : 0);
            categoryData.add(loan);
            
            Map<String, Object> service = new HashMap<>();
            service.put("name", "农服");
            service.put("value", serviceCount != null ? serviceCount : 0);
            categoryData.add(service);
            
            result.put("categoryData", categoryData);
            
            return Result.success(result);
        } catch (Exception e) {
            e.printStackTrace();
            return Result.error("获取分布数据失败");
        }
    }

    /**
     * 获取月度趋势数据
     */
    @GetMapping("/monthlyTrend")
    public Result<Map<String, Object>> getMonthlyTrend() {
        try {
            Map<String, Object> trend = new HashMap<>();
            
            // 生成最近12个月的数据
            List<String> months = new ArrayList<>();
            List<Integer> sales = new ArrayList<>();
            List<Integer> browse = new ArrayList<>();
            
            Calendar calendar = Calendar.getInstance();
            for (int i = 11; i >= 0; i--) {
                calendar.add(Calendar.MONTH, -i);
                int month = calendar.get(Calendar.MONTH) + 1;
                months.add(month + "月");
                
                // 模拟数据：随机生成销量和浏览量趋势数据
                sales.add((int)(Math.random() * 100) + 50);
                browse.add((int)(Math.random() * 200) + 100);
                
                calendar = Calendar.getInstance();
            }
            
            trend.put("months", months);
            trend.put("sales", sales);
            trend.put("browse", browse);
            
            return Result.success(trend);
        } catch (Exception e) {
            e.printStackTrace();
            return Result.error("获取趋势数据失败");
        }
    }
}

