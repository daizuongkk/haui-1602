import {
  CloudRain,
  Waves,
  Snowflake,
  CloudFog,
  Zap,
  Wind,
  CloudHail,
  TriangleAlert,
  type LucideIcon,
} from "lucide-react";

// Map tên hiểm họa (backend) -> icon + khuyến cáo an toàn CHUNG.
// Đây là nội dung an toàn tĩnh áp dụng cho mọi cảnh báo cùng loại,
// không phải dữ liệu bịa theo từng địa điểm.
interface HazardInfo {
  icon: LucideIcon;
  do: string[];
  dont: string[];
}

const RULES: { match: RegExp; info: HazardInfo }[] = [
  {
    match: /lũ|ngập|sạt|taluy/i,
    info: {
      icon: Waves,
      do: [
        "Chuẩn bị giấy tờ, thuốc men, đồ dùng thiết yếu",
        "Di chuyển người già, trẻ nhỏ, vật nuôi lên nơi cao",
        "Theo dõi thông báo của chính quyền địa phương",
      ],
      dont: [
        "Không đi qua suối, ngầm tràn khi nước dâng",
        "Không đến gần taluy, sườn dốc có nguy cơ sạt lở",
        "Không quay lại vùng nguy hiểm khi chưa an toàn",
      ],
    },
  },
  {
    match: /mưa/i,
    info: {
      icon: CloudRain,
      do: [
        "Kiểm tra, khơi thông thoát nước quanh nhà",
        "Hạn chế ra ngoài khi mưa lớn",
        "Sạc đầy điện thoại, chuẩn bị đèn pin",
      ],
      dont: ["Không trú mưa dưới cây to, cột điện", "Không lội qua vùng nước chảy xiết"],
    },
  },
  {
    match: /dông|lốc|sét/i,
    info: {
      icon: Zap,
      do: ["Vào nhà kiên cố, tránh nơi trống trải", "Rút phích điện thiết bị khi có sét"],
      dont: ["Không trú dưới cây cao, gò đất", "Không dùng điện thoại có dây khi sấm sét"],
    },
  },
  {
    match: /gió|bão/i,
    info: {
      icon: Wind,
      do: ["Gia cố mái nhà, chằng chống cửa", "Đưa vật nuôi vào nơi trú an toàn"],
      dont: ["Không đứng gần cây, biển quảng cáo", "Không ra khơi, ra sông suối"],
    },
  },
  {
    match: /mưa đá|hail/i,
    info: {
      icon: CloudHail,
      do: ["Trú ẩn trong nhà kiên cố", "Che chắn phương tiện, cây trồng"],
      dont: ["Không ra ngoài khi đang có mưa đá"],
    },
  },
  {
    match: /rét|lạnh|frost|sương muối/i,
    info: {
      icon: Snowflake,
      do: ["Giữ ấm cho người già, trẻ nhỏ", "Che chắn, sưởi ấm cho gia súc, cây trồng"],
      dont: ["Không đốt than sưởi trong phòng kín", "Không cho gia súc ra ngoài ban đêm"],
    },
  },
  {
    match: /sương mù|mù/i,
    info: {
      icon: CloudFog,
      do: ["Bật đèn khi tham gia giao thông", "Đi chậm, giữ khoảng cách an toàn"],
      dont: ["Không vượt xe khi tầm nhìn hạn chế"],
    },
  },
];

export function hazardIcon(name: string): LucideIcon {
  return RULES.find((r) => r.match.test(name))?.info.icon ?? TriangleAlert;
}

// Gộp khuyến cáo từ tất cả hiểm họa đang có (khử trùng lặp).
export function safetyAdvice(hazardNames: string[]): { do: string[]; dont: string[] } {
  const doSet = new Set<string>();
  const dontSet = new Set<string>();
  for (const name of hazardNames) {
    const info = RULES.find((r) => r.match.test(name))?.info;
    info?.do.forEach((x) => doSet.add(x));
    info?.dont.forEach((x) => dontSet.add(x));
  }
  if (doSet.size === 0) doSet.add("Theo dõi thông báo của chính quyền địa phương");
  return { do: [...doSet], dont: [...dontSet] };
}
