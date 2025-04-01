#include <iostream>
#include <fstream>
#include <vector>
#include <optional>
#include <boost/asio/ip/address.hpp>
#include <boost/algorithm/string.hpp>
namespace Address
{
    using namespace boost::asio::ip;
    using namespace boost::algorithm;
    using namespace std;
    typedef pair<std::string, std::string> DataPair;

    vector<address> ipv4;
    vector<address> ipv6;
    vector<DataPair> ipv4data;
    vector<DataPair> ipv6data;

    void read_file(const std::string &filename, vector<DataPair> &data, vector<address> &ip)
    {
        ifstream _file(filename);
        std::string line;

        size_t num_lines = count(istreambuf_iterator<char>(_file), istreambuf_iterator<char>(), '\n');
        // 重置文件流
        _file.clear();
        _file.seekg(0, ios::beg);

        ip.reserve(num_lines);
        data.reserve(num_lines);
        while (getline(_file, line))
        {
            vector<std::string> row;
            split(row, line, is_any_of("\t"));

            ip.push_back(make_address(row[0]));
            data.emplace_back(row[2], row[4]);

            if (_file.peek() == EOF)
            {
                ip.push_back(make_address(row[1]));
                break;
            }
        }
        _file.close();
    }

    void init(const std::string &ipv4file, const std::string &ipv6file)
    {
        read_file(ipv4file, ipv4data, ipv4);
        read_file(ipv6file, ipv6data, ipv6);
        if (ipv4.empty() || ipv6.empty())
        {
            cout << "\033[31m"
                 << "Error: ipasn.hpp: init(): ipv4 or ipv6 file is empty, Please go to https://iptoasn.com/ and download the latest files."
                 << endl
                 << "ipv4 file: Please download the latest version file from https://iptoasn.com/data/ip2asn-v4.tsv.gz and unzip it."
                 << endl
                 << "ipv6 file: Please download the latest version file from https://iptoasn.com/data/ip2asn-v6.tsv.gz and unzip it."
                 << "\033[0m" << endl;
        }
        else
        {
            cout << "\033[32m\033[1m"
                 << "ipasn.hpp: init(): ipv4 and ipv6 file loaded" << endl;
            cout << "ipasn.hpp: init(): ipv4 size: "
                 << "\033[4m" << ipv4.size() << "\033[0m" << endl;
            cout << "\033[32m\033[1m"
                 << "ipasn.hpp: init(): ipv6 size: "
                 << "\033[4m" << ipv6.size() << "\033[0m" << endl;
        }
    }

    inline std::optional<size_t> binary_search(vector<address> &data, const address &ip)
    {
        auto it = lower_bound(data.begin(), data.end(), ip);
        if (it == data.begin() || it == data.end())
        {
            return std::nullopt;
        }
        return distance(data.begin(), std::prev(it));
    }

    DataPair lookup(const std::string &ip)
    {
        address _ip = make_address(ip);
        bool is_ipv4 = _ip.is_v4();

        auto &&[target_ip, target_data] = is_ipv4 ? std::tie(ipv4, ipv4data) : std::tie(ipv6, ipv6data);

        if (auto index = binary_search(target_ip, _ip))
        {
            return target_data.at(*index);
        }

        throw std::runtime_error("IP not found");
    }

}